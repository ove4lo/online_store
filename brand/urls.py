from django.urls import path, include
from django.contrib import admin
from .views import *

urlpatterns = [
    path('brand/', get_all_brands)
]