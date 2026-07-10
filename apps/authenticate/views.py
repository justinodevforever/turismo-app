from django.shortcuts import render
from apps.empresas.models import *
from apps.provincias.models import *

# Create your views here.
def index(request):
    
    provincias        = Provincia.objects.all().order_by('ordem')
    pontos_toristicos = PontoTuristico.objects.all()
    gastronomias      = PratoTipico.objects.all()
    hoteis            = Hotel.objects.all()
    guias             = GuiaTuristico.objects.all()
    prato_destaque    = PratoTipico.objects.filter(destaque=True).first()
    ponto_destaque    = PontoTuristico.objects.filter(destaque=True).first()
    
    #ponto_toristico_destaque = PontoTuristico.objects.filter(total_visualizacoes=)
    
    context = {
        'pontos_toristicos': pontos_toristicos,
        'provincias':        provincias,
        'gastronomias':      gastronomias,
        'hoteis':            hoteis,
        'guias':             guias,
        'secao':             'home',
        'prato_destaque':    prato_destaque,
        'ponto_destaque':    ponto_destaque,
    }
    
    return render(request, "pagebase/index.html", context)