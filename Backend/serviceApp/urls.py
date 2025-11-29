from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('',home, name='home'),
    path('granted/',service_granted, name='service_granted'),
]
