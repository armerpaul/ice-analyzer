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
    code_set = set()

    if card_codes_param_string:
        code_set = set(card_codes_param_string.split(LIST_DELIM))

    ice_list = Ice.objects.filter(code__in=code_set)
    breaker_list = Breaker.objects.filter(code__in=code_set)

    # If there were no ice or no breakers in provided code set, 
    # use a default set for the empty list

    if not ice_list or ice_list.count() < 1:
        ice_list = Ice.objects.filter(code__in=DEFAULT_ICE_CODES)

    if not breaker_list or breaker_list.count() < 1:
        breaker_list = Breaker.objects.filter(code__in=DEFAULT_BREAKER_CODES)

    break_data = {}

    for ice in ice_list:
        break_data_for_ice = {}

        for breaker in breaker_list:
            break_data_for_ice[breaker.code] = breaker.cost_to_break(ice)

        break_data[ice.code] = break_data_for_ice

    return JsonResponse(break_data)


def default_cards(request):
    ice_list = Ice.objects.filter(code__in=DEFAULT_ICE_CODES)
    breaker_list = Breaker.objects.filter(code__in=DEFAULT_BREAKER_CODES)

    card_data = {}
    for card in (list(ice_list) + list(breaker_list)):
        card_data[card.code] = card.as_json()

    return JsonResponse(card_data)

def card_search(request):
    query_str = request.GET.get('q')
    if not query_str:
        return JsonResponse({
            "error": "'name' is a required query param"
        })

    ice_list = Ice.objects.filter(name__contains=query_str)
    ice_count = ice_list.count()
    if ice_count == 1:
        return JsonResponse(ice_list.first().as_json())

    breaker_list = Breaker.objects.filter(name__contains=query_str)
    if breaker_list.count() == 1:
        return JsonResponse(breaker_list.first().as_json())

    total_results = ice_count + breaker_count
    error_msg = "No card found for query: %s"
    if total_results > 1: 
        error_msg = "More than 1 card found for query: %s"

    return JsonResponse({
        "error": error_msg % query_str
    })


def card_by_code(request, code):
    ice = Ice.objects.filter(code=code)
    if ice.count() == 1:
        return JsonResponse(ice.first())

    breaker = Breaker.objects.filter(code=code)
    if breaker.count() == 1:
        return JsonResponse(breaker.first())

    return JsonResponse({
        "error": "No breaker or ice found with code %s" % code
    })
