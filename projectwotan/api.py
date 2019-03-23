from django.shortcuts import render
from django.http import JsonResponse
from .models import Ice, Breaker
from .shortcuts import log

DEFAULT_ICE_CODES = (
    # HB
    "25073", # Eli 1.0
    "11049", # Fairchild 3.0
    "06061", # Architect
    # Jinteki
    "12013", # Kakugo
    "11053", # DNA Tracker
    "21051", # Anansi
    # NBN
    "11094", # IP Block
    "25115", # Tollbooth
    "09014", # News Hound
    # Weyland
    "23054", # Border Control
    "25133", # Hortum
    "25130", # Archer
    # Neutral
    "10095", # Vanilla
    "25143", # Enigma
    "10074", # Cobra
)
DEFAULT_BREAKER_CODES = (
    # Anarch
    "25010", # Corroder
    "11042", # Black Orchestra
    "11081", # MK Ultra
    # Criminal
    "11064", # Saker
    "21104", # Anima
    "26016", # Bukhgalter
    # Shaper
    "26024", # Gauss
    "25054", # Gordian Blade
    "12088", # Na'Not'K
)

LIST_DELIM = ','

def break_costs(request):
    # If request data has ice codes, key by ice, otherwise key by breakers
    # Assign break data generation function based on above result
    card_codes_param_string = request.GET.get('codes')
    code_set = None

    if card_codes_param_string:
        code_set = set(card_codes_param_string.split(LIST_DELIM))

    ice_code_set = code_set or DEFAULT_ICE_CODES
    breaker_code_set = code_set or DEFAULT_BREAKER_CODES

    ice_list = Ice.objects.filter(code__in=ice_code_set)
    breaker_list = Breaker.objects.filter(code__in=breaker_code_set)

    break_data = {}

    for breaker in breaker_list:
        break_data_for_breaker = {}

        for ice in ice_list:
            break_data_for_breaker[ice.code] = breaker.cost_to_break(ice)

        break_data[breaker.code] = break_data_for_breaker

    return JsonResponse(break_data)
