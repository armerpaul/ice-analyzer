import urllib.request as request
import json

from projectwotan.models import (
    Breaker,
    Ice,
)

OUTPUT_FILE_NAME = 'break-costs.json'

RELOAD_FROM_NRDB = True
VERBOSE = False
OUTPUT_BREAKERS = False
OUTPUT_ICE = False

# Update Cards
if RELOAD_FROM_NRDB:

    API_VERSION = "2.0"
    API_CARD_URL = "https://netrunnerdb.com/api/%s/public/cards" % API_VERSION

    response = request.urlopen(API_CARD_URL)
    html = response.read()
    data = json.loads(html)

    def is_valid_ice(data):
        return "ice" in data["type_code"]

    def is_valid_breaker(data):
        if "program" in data["type_code"]:
            if "keywords" in data and "Icebreaker" in data["keywords"]:
                return True

        return False

    def log(created, name, pk, code):
        if VERBOSE:
            print("[%s] %s (pk = %s, code = %s)" % (
                "Create" if created else "Updated",
                name,
                pk,
                code,
            ))

    deduped_card_data = {}
    for card_data in data["data"]:  
        name = card_data["title"]

        if name not in deduped_card_data or card_data["code"] > deduped_card_data[name]["code"]:
            deduped_card_data[name] = card_data

    for name, card_data in deduped_card_data.items():  
        try:
            if is_valid_ice(card_data):
                ice, created = Ice.objects.get_or_create(code=card_data["code"])
                ice.extend(card_data)

                log(created, ice.name, ice.pk, ice.code)
                ice.save()

            if is_valid_breaker(card_data):
                breaker, created = Breaker.objects.get_or_create(code=card_data["code"])
                breaker.extend(card_data)

                log(created, breaker.name, breaker.pk, breaker.code)
                breaker.save()
        
        except Exception:
            print("Error processing card [%s]" % card_data["code"])
            print(card_data)

# Test
if OUTPUT_BREAKERS:
    for breaker in Breaker.objects.all():
        print("\n%s" % breaker.name)
        print(" Breaks: %s" % breaker.stats['break_type'])

        if 'break_cost' in breaker.stats:
            print(" %sc: %ssub(s)" % (breaker.stats['break_cost'], breaker.stats['break_amount'],))
        if 'boost_cost' in breaker.stats:
            print(" %sc: +%s" % (breaker.stats['boost_cost'], breaker.stats['boost_amount'],))
        

if OUTPUT_ICE:
    for ice in Ice.objects.all():
        print("\n%s" % ice.name)
        print(" Cost: %s | Str: %s" % (ice.cost, ice.strength,))
        print(" %s" % ice.keywords)

        for sub in ice.subroutines:
            print(" -> %s" % sub.text)


    