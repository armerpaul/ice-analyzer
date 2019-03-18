from django.urls import path, include

from django.contrib import admin

admin.autodiscover()

from . import views

# To add a new path, first import the app:
# import blog
#
# Then add the new path:
# path('blog/', blog.urls, name="blog")
#
# Learn more here: https://docs.djangoproject.com/en/2.1/topics/http/urls/

urlpatterns = [
    path("breakers/<str:breakers>/", views.filter_breakers_and_ice),
    path("breakers/<str:breakers>/ice/<str:ice>/", views.filter_breakers_and_ice),
    path("ice/<str:ice>/", views.filter_ice_and_breakers),
    path("ice/<str:ice>/breakers/<str:breakers>/", views.filter_ice_and_breakers),
    path("", views.index),
]
