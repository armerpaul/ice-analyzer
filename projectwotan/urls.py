from django.urls import path, include

from django.contrib import admin

admin.autodiscover()

from . import views, api

# To add a new path, first import the app:
# import blog
#
# Then add the new path:
# path('blog/', blog.urls, name="blog")
#
# Learn more here: https://docs.djangoproject.com/en/2.1/topics/http/urls/

urlpatterns = [
    # API Endpoints
    path("api/break-costs/", api.break_costs),
    path("api/cards/search/", api.card_search),
    path("api/cards/default/", api.default_cards),

    # Views
    path("", views.index),
    path("about/", views.about),
]
