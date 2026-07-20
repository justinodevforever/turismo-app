from django.urls import path
from .views import *

urlpatterns = [
    
    path('provincias/', provincias, name='provincias'),
    path('provincias/<uuid:provincia_id>/detalhe', provincia_detalhe, name='provincia_detalhe'),

    # Página do Assistente IA
    path(
        'assistente-ia/',
        AssistenteIAView.as_view(),
        name='assistente_ia'
    ),

    # Endpoint AJAX para enviar perguntas
    path(
        'assistente-ia/perguntar/',
        AssistenteIAPerguntarView.as_view(),
        name='assistente_ia_perguntar'
    ),

]