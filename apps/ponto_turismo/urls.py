from django.urls import path
from .views import *

urlpatterns = [
    path("ponto-turistico/", ponto_turistico, name='ponto_turistico'),
    path('ponto-turistico/<int:id>/', ponto_turistico_detalhe, name='ponto_turistico_detalhe'),
    path("guia-turistico/", guia_turistico, name='guia_turistico'),
    
    
    path('api_guia_turistico/<int:id>/', api_guia_turistico, name='api_guia_turistico')
]