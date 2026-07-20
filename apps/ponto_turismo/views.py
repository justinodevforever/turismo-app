from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from apps.provincias.models import *
from apps.empresas.models import *
import json
from django.core.paginator import Paginator

# Create your views here.
def ponto_turistico(request):
    
    pontos_turisticos = PontoTuristico.objects.all()
    provincas = Provincia.objects.all()
    
    per_page = request.GET.get('per_page', 20)
    page     = request.GET.get('page', 1)
    entrada    = request.GET.get('entrada')
    provincia = request.GET.get('provincia')
    search    = request.GET.get('search')
    
    if provincia:
        
        pontos_turisticos = pontos_turisticos.filter(provincia__nome=provincia)
        
    if search:
        
        pontos_turisticos = pontos_turisticos.filter(nome__icontains=search)
        
    if entrada == 'gratuito':
        pontos_turisticos = pontos_turisticos.filter(entrada_gratuita=True)
    elif entrada == 'pago':
        pontos_turisticos = pontos_turisticos.filter(entrada_gratuita=False)
    
    paginator           = Paginator(pontos_turisticos, per_page)
    pontos_turisticos   = paginator.page(page)
    
    context = {
        'per_page': per_page,
        'provincas': provincas,
        'page': page,
        'provincia': provincia,
        'entrada': entrada,
        'pontos_turisticos': pontos_turisticos,
        'secao': 'ponto_turistico'
    }
    
    return render(request, "turismo/pontos_turisticos.html", context)

def ponto_turistico_detalhe(request, id):
    
    ponto_turistico = PontoTuristico.objects.get(id=id)
    
    ponto_turistico.total_visualizacoes = ponto_turistico.total_visualizacoes + 1
    
    ponto_turistico.save()

    
    context = {
        'ponto_turistico': ponto_turistico,
        'secao': 'ponto_turistico'
    }
    
    return render(request, "turismo/pontos_turisticos_detalhes.html", context)

def guia_turistico(request):
    
    guias_turisticos = GuiaTuristico.objects.all()
    #total_guia_certificado = GuiaTuristico.objects.filter()
    provincias = Provincia.objects.all()
    
    per_page = request.GET.get('per_page', 20)
    page     = request.GET.get('page', 1)
    nivel    = request.GET.get('nivel')
    idioma   = request.GET.get('nivel')
    provincia = request.GET.get('nivel')
    search    = request.GET.get('search')
    
    nome_provincia = request.GET.get('provincia')
    
    if nome_provincia:
        guias_turisticos = guias_turisticos.filter(empresa__provincia__nome=nome_provincia)
    
    paginator           = Paginator(guias_turisticos, per_page)
    guias_turisticos    = paginator.page(page)
    
    
    context = {
        'guias_turisticos': guias_turisticos,
        'provincias': provincias,
        'per_page': per_page,
        'page': page,
        'nivel': nivel,
        'idioma': idioma,
        'provincia': provincia,
        'search': search,
        'secao': 'guia'
    }
    
    return render(request, "turismo/guia_turistico.html", context)

def api_guia_turistico(request, id):
    
    try:
        
        guia = GuiaTuristico.objects.get(id=id)
        
        provincias = []
        
        for p in guia.provincias_atuacao.all():
            
            provincias.append(p.nome)
        
        
        dados = {
            'nome': guia.usuario.nome_completo,
            'empresa': guia.empresa.nome,
            'nivel_esperiencia': guia.get_nivel_experiencia_display(),
            'idiomas': guia.idiomas,
            'provincias': provincias,
            'anos_experiencia': guia.anos_experiencia,
            'foto': guia.foto.url,
            'especializacoes': guia.especializacoes,
            'preco_hora': guia.preco_hora,
            'preco_completo': guia.preco_dia_completo,
            'disponibilildade': guia.disponivel,
            'total_excursoes': guia.total_excursoes,
            'total_avaliacao': guia.total_avaliacoes
        }
    
        return JsonResponse(dados, status=200)
    
    except GuiaTuristico.DoesNotExist:
        return JsonResponse({'message': 'Erro ao Carregar os dados'}, status=500)