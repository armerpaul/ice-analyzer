from django.db import models
import re
import math

class Card(models.Model):
    DEFAULT_IMG_URL_TEMPLATE = "https://netrunnerdb.com/card_image/%s.png"
    VARIABLE_STRENGTH = -1

    NISEI_PACKS = (
        'df'
    )

    keywords = models.TextField()
    name = models.CharField(max_length=128)
    text = models.TextField()
    code = models.CharField(max_length=5)
    cost = models.IntegerField(default=0)
    strength = models.IntegerField(default=VARIABLE_STRENGTH)
    image = models.TextField(default="")
    is_nisei = models.BooleanField(default=False)

    def extend(self, data):
        self.keywords = data["keywords"]
        self.name = data["title"]
        self.text = data.get("text", "")
        self.code = data["code"]
        self.cost = int(data["cost"])
        self.strength = self.VARIABLE_STRENGTH
        self.image = data.get("image_url", self.default_img_url)
        self.is_nisei = data["pack_code"] in self.NISEI_PACKS

        if "strength" in data and data["strength"]:
            self.strength = int(data["strength"])

    def as_json(self):
       return {
           "name": self.name,
           "code": self.code,
           "text": self.text,
           "cost": self.cost,
           "strength": self.strength,
           "subtypes": self.subtypes,
           "image": self.image,
           "type": self.__class__.__name__.lower(),
           "isNisei": self.is_nisei
       }

    @property
    def is_strength_variable(self):
        return self.strength is self.VARIABLE_STRENGTH

    @property
    def subtypes(self):
        return self.keywords.lower().split(" - ")

    @property
    def default_img_url(self):
        return self.DEFAULT_IMG_URL_TEMPLATE % self.code

    class Meta:
        abstract = True

class Breaker(Card):
    BREAK_LINE_PATTERN = "([\d])\[credit]: [Bb]reak"
    BOOST_LINE_PATTERN = "(\d)\[credit]: \+(\d) strength"

    ALL_ICE_TYPES = '*'
    TYPE_MISMATCH = -1
    CANNOT_BOOST = -2
    PARSE_ERROR = -666
        
    @property
    def stats(self):
        stats = {}
        lines = self.text.split('\n')

        stats['break_type'] = self.ALL_ICE_TYPES

        for line in lines:
            break_match = re.search(self.BREAK_LINE_PATTERN, line)
            boost_match = re.search(self.BOOST_LINE_PATTERN, line)

            if break_match:
                stats['break_line'] = line
                stats['break_cost'] = int(break_match.group(1))
                stats['break_amount'] = 1
                
                # Infinite subs
                if "any number of" in line:
                    stats['break_amount'] = math.inf
                
                # Some non-1 number
                amount_match = re.search("up to (\d)", line)
                if amount_match:
                    stats['break_amount'] = int(amount_match.group(1))

                # ICE Type
                ice_type_match = re.search("<strong>([\w ]+)</strong>", line)
                if ice_type_match:
                    stats['break_type'] = ice_type_match.group(1).lower()

            elif boost_match:
                stats['boost_line'] = line
                stats['boost_cost'] = int(boost_match.group(1))
                stats['boost_amount'] = int(boost_match.group(2))
            
        return stats

    def cost_to_break(self, ice):
        break_type = self.stats['break_type']
        if break_type not in ice.subtypes and break_type is not self.ALL_ICE_TYPES:
            return self.TYPE_MISMATCH

        total_boost_cost = 0
        if not self.is_strength_variable and not ice.is_strength_variable:
            amount_to_boost = ice.strength - self.strength

            if amount_to_boost > 0:
                if not self.can_boost:
                    return self.CANNOT_BOOST

                times_to_boost = math.ceil(amount_to_boost / self.stats['boost_amount'])
                total_boost_cost = times_to_boost * self.stats['boost_cost']

        # TODO Remove after improving text decoding
        if 'break_amount' not in self.stats or 'break_cost' not in self.stats:
            return self.PARSE_ERROR

        subroutine_count = len(ice.subroutines)
        times_to_break = math.ceil(subroutine_count / self.stats['break_amount'])
        total_break_cost = times_to_break * self.stats['break_cost']

        return total_boost_cost + total_break_cost

    @property
    def can_boost(self):
        return 'boost_cost' in self.stats and 'boost_amount' in self.stats 


class Ice(Card):
    class Subroutine(object):
        PREFIX = '[subroutine]'
        TRACE_PATTERN = '<trace>trace ([X\d])</trace>'
        ETR_PATTERN = '[Ee]nd the run'
        ETR_UNLESS_COST_PATTERN = 'End the run unless the Runner pays (\d)[credit]'
        ETR_IF_TAGGED = 'End the run if the Runner is tagged'

        def __init__(self, line):
            self.text = line.replace(self.PREFIX, '').strip()

        @property
        def is_trace(self):
            return re.search(self.TRACE_PATTERN, self.text) is not None

        @property
        def trace_strength(self):
            match = re.search(self.TRACE_PATTERN, self.text)
            return match.group(1) if match else None

        @property
        def can_end_the_run(self):
            return re.search(self.ETR_PATTERN, self.text) is not None

        @property
        def alternative_cost(self):
            match = re.search(self.ETR_UNLESS_COST_PATTERN, self.text)
            return match.group(1) if match else None

        def applies_to_runner(self, runner):
            if not runner.get('tagged', False) and self.ETR_IF_TAGGED in self.text:
                return False

            return True

        def as_json(self):
            data = {
                'text': self.text,
                'etr': self.can_end_the_run
            }

            if self.is_trace:
                data['trace'] = self.trace_strength

            return data

        @classmethod
        def is_subroutine(cls, line):
            return cls.PREFIX in line

    def extend(self, data):
        super().extend(data)

    @property
    def subroutines(self):
        lines = self.text.split('\n')

        subroutines = []

        for line in lines:
            if self.Subroutine.is_subroutine(line):
                subroutines.append(self.Subroutine(line))

        return subroutines

    def as_json(self):
        data = super().as_json()

        data['subroutines'] = [s.as_json() for s in self.subroutines]

        return data
