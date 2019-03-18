from django.shortcuts import render
from django.http import HttpResponse

from .models import Greeting

def filter_breakers_and_ice(request, breakers, ice=None):
    return _filter(request=request, breakers=breakers, ice=ice)

def filter_ice_and_breakers(request, ice, breakers=None):
    return _filter(request=request, breakers=breakers, ice=ice)

def index(request):
    return _filter(request=request)

LIST_DELIM = ","

def _filter(request=None, breakers=None, ice=None):
    ice_list = set(ice.split(LIST_DELIM) if ice else []) # TODO: All ICE
    breaker_list = set(breakers.split(LIST_DELIM) if breakers else []) # TODO: All breakers

    context = {
        'breakers': breaker_list,
        'ice': ice_list,
    }

    return render(request, "break_cost_table.html", context)