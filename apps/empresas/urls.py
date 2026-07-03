from django.urls import path
from .views import *

urlpatterns = [
    path('gastronomias/', gastronomia_lista, name='gastronomia_lista'),
    path('alojamentos/', alojamento_lista, name="alojamento_lista"),
    path('restaurantes', restaurante_lista, name='restaurante_lista')
]
