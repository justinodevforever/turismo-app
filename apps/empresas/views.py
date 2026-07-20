from django.shortcuts import render
from .models import *
from apps.provincias.models import *
from django.core.paginator import Paginator

# Create your views here.
def gastronomia_lista(request):
    
    provincia = request.GET.get('provincia')
    gastronomias    = PratoTipico.objects.all()
    prato_destaque  = PratoTipico.objects.filter(destaque=True).first()
    provincias      = Provincia.objects.all()
    
    if provincia:
        gastronomias = gastronomias.filter(provincia__nome=provincia)
    
    context = {
        'gastronomias': gastronomias,
        'provincias': provincias,
        'prato_destaque':prato_destaque,
        'secao': 'gastronomia',
    }
    
    return render(request, "gastronomia/gastronomia.html", context)

# Create your views here.
def alojamento_lista(request):
    
    hoteis     = Hotel.objects.all()
    provincias = Provincia.objects.all()
    
    page        = request.GET.get('page', 1)
    per_page    = request.GET.get('per_page', 20) 
    provincia   = request.GET.get('provincia')
    nome_provincia   = request.GET.get('nome_provincia')
    check_in    = request.GET.get('check_in ')
    check_out   = request.GET.get('check_out')
    order_by   = request.GET.get('order_by')
    
    if provincia:
        
        hoteis = hoteis.filter(empresa__provincia=provincia)
        
    if nome_provincia:
        
        hoteis = hoteis.filter(empresa__provincia__nome=nome_provincia)
        
    if check_in:
        
        hoteis = hoteis.filter(check_in=check_in)
    
    if check_out:
        
        hoteis = hoteis.filter(check_out=check_out)
        
    if order_by:
        
        hoteis = hoteis.order_by(preco_min_noite=order_by)
    
    paginator   = Paginator(hoteis, per_page)
    hoteis  = paginator.page(page)
    
    context = {
        'hoteis': hoteis,
        'provincias': provincias,
        'per_page': per_page,
        'page': page,
        'secao': 'alojamento'
    }
    
    return render(request, "alojamentos/alojamento.html", context)

# Create your views here.
def restaurante_lista(request):
    
    restaurantes    = Restaurante.objects.all()
    total_restaurate = restaurantes.count()
    menus           = ItemMenu.objects.all()
    total_provincia = Provincia.objects.count()
    
    page        = request.GET.get('page', 1)
    per_page    = request.GET.get('per_page', 20) 
    tipo_cozinha   = request.GET.get('tipo_cozinha')
    search    = request.GET.get('search')
    order_by   = request.GET.get('order_by')
    
    if tipo_cozinha:
        
        restaurantes = restaurantes.filter(tipo_cozinha=tipo_cozinha)
        
    if not order_by == 'todos' and order_by:
        
        restaurantes = restaurantes.filter(faixa_preco=order_by)
    
    paginator   = Paginator(restaurantes, per_page)
    restaurantes  = paginator.page(page)
    
    context = {
        'restaurantes': restaurantes,
        'menus': menus,
        'total_provincia': total_provincia,
        'total_restaurate': total_restaurate,
        'per_page': per_page,
        'page': page,
        'order_by': order_by,
        'tipos': Restaurante.TipoCozinha.choices,
        'secao': 'alojamento'
    }
    
    return render(request, "alojamentos/restaurante.html", context)