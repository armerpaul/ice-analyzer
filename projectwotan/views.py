from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    context = {
        
    }
    return render(request, "break_cost_table.html", context)

def about(request):
    context = {
        
    }
    return render(request, "about.html", context)
