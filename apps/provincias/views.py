"""
============================================================
EXPLORA REGIÃO AI — apps/provincias/views.py (adicionar)
Assistente IA — Chat com Inteligência Artificial
============================================================

Estas views destinam-se a ser acrescentadas ao ficheiro
`apps/provincias/views.py` já existente (juntar os imports do
topo aos imports já lá presentes).

Rotas sugeridas (ver `urls.py` no fim deste ficheiro, em comentário):
    /assistente-ia/                 -> AssistenteIAView          (GET)
    /assistente-ia/perguntar/        -> AssistenteIAPerguntarView (POST, AJAX)
"""

import json
import logging
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.views.generic import TemplateView

from .models import *
from apps.empresas.models import *

logger = logging.getLogger(__name__)

try:
    import anthropic
except ImportError:  # a dependência pode ainda não estar instalada
    anthropic = None

def provincias(request):
    
    provincias = Provincia.objects.all()
    
    context = {
        'provincias': provincias,
        'secao': 'provincia'
    }
    
    for p in provincias:
        print(p.id)
    
    return render(request, "provincias/provincia.html", context)

def provincia_detalhe(request, provincia_id):
    
    provincia          = Provincia.objects.get(id=provincia_id)
    municipios         = Municipio.objects.filter(provincia=provincia)
    gastronomias       = PratoTipico.objects.filter(provincia=provincia)
    pontos_turisticos  = PontoTuristico.objects.filter(provincia=provincia)
    hoteis             = Hotel.objects.filter(empresa__provincia=provincia)
    guias              = GuiaTuristico.objects.filter(empresa__provincia=provincia)
    
    context = {
        'provincia': provincia,
        'municipios': municipios,
        'gastronomias': gastronomias,
        'pontos_turisticos': pontos_turisticos,
        'hoteis': hoteis,
        'guias': guias,
        'secao': 'provincia'
    }
    
    return render(request, "provincias/provincia_detalhes.html", context)

# ============================================================
# PÁGINA DO ASSISTENTE IA
# ============================================================

class AssistenteIAView(LoginRequiredMixin, TemplateView):
    """
    Renderiza a página de chat com o Assistente IA.

    Mostra o histórico recente de conversas do utilizador autenticado
    e algumas sugestões de perguntas/províncias para começar a conversa.
    """
    template_name = 'provincias/assistente_ia.html'
    login_url = '/conta/entrar/'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)

        historico = list(
            ConversaAI.objects
            .filter(usuario=self.request.user)
            .order_by('-criado_em')[:20]
        )
        historico.reverse()  # mostrar do mais antigo para o mais recente
        contexto['historico'] = historico

        contexto['provincias_sugestao'] = (
            Provincia.objects
            .filter(status=Provincia.Status.PUBLICADO)
            .order_by('nome')
            .values_list('nome', flat=True)
        )

        contexto['perguntas_sugeridas'] = [
            'Quais são as melhores praias de Angola?',
            'Conta-me sobre as Quedas de Kalandula.',
            'Que pratos típicos devo experimentar em Luanda?',
            'Qual é a melhor época para visitar o Namibe?',
        ]
        return contexto


# ============================================================
# ENDPOINT DE CONVERSA (AJAX)
# ============================================================

@method_decorator(csrf_protect, name='dispatch')
class AssistenteIAPerguntarView(LoginRequiredMixin, View):
    """
    Recebe a pergunta do utilizador via POST (JSON), monta um contexto
    a partir de dados reais da base de dados (Províncias, Pontos
    Turísticos e Pratos Típicos — uma espécie de RAG simplificado) e
    consulta o modelo de IA, devolvendo a resposta em JSON.

    A conversa é sempre gravada em `ConversaAI` para histórico e
    auditoria.
    """
    LIMITE_RESULTADOS = 5
    TAMANHO_MAX_PERGUNTA = 1000

    def post(self, request, *args, **kwargs):
        try:
            dados = json.loads(request.body.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({'erro': 'Pedido inválido.'}, status=400)

        pergunta = (dados.get('pergunta') or '').strip()
        if not pergunta:
            return JsonResponse({'erro': 'A pergunta não pode estar vazia.'}, status=400)
        if len(pergunta) > self.TAMANHO_MAX_PERGUNTA:
            return JsonResponse({'erro': 'A pergunta é demasiado longa.'}, status=400)

        contexto_bd = self._montar_contexto(pergunta)

        try:
            resposta_texto = self._consultar_ia(pergunta, contexto_bd)
        except Exception:
            logger.exception('Falha ao consultar o Assistente IA (pergunta=%r)', pergunta)
            return JsonResponse(
                {'erro': 'Não foi possível obter resposta do assistente. Tenta novamente dentro de momentos.'},
                status=503,
            )

        ConversaAI.objects.create(
            usuario=request.user,
            pergunta=pergunta,
            resposta=resposta_texto,
            contexto=contexto_bd,
        )

        return JsonResponse({'resposta': resposta_texto, 'contexto': contexto_bd})

    # --------------------------------------------------------
    # Construção do contexto a partir da base de dados
    # --------------------------------------------------------
    def _montar_contexto(self, pergunta):
        """
        Pesquisa, por palavras-chave da pergunta, Províncias, Pontos
        Turísticos e Pratos Típicos relacionados, para servirem de
        contexto factual ao modelo de IA (evita que a IA "invente"
        dados sobre Angola que não existem na plataforma).
        """
        termos = [termo for termo in pergunta.lower().split() if len(termo) > 3][:6]

        provincias = Provincia.objects.filter(status=Provincia.Status.PUBLICADO)
        pontos = PontoTuristico.objects.filter(status=PontoTuristico.Status.PUBLICADO)
        pratos = PratoTipico.objects.filter(status=PratoTipico.Status.PUBLICADO)

        if termos:
            filtro_provincias = Q()
            filtro_pontos = Q()
            filtro_pratos = Q()

            for termo in termos:
                filtro_provincias |= (
                    Q(nome__icontains=termo) | Q(introducao__icontains=termo) |
                    Q(historia__icontains=termo) | Q(cultura__icontains=termo) |
                    Q(patrimonio__icontains=termo) | Q(gastronomia__icontains=termo)
                )
                filtro_pontos |= (
                    Q(nome__icontains=termo) | Q(descricao__icontains=termo) |
                    Q(historia__icontains=termo)
                )
                filtro_pratos |= (Q(nome__icontains=termo) | Q(descricao__icontains=termo))

            provincias = provincias.filter(filtro_provincias)
            pontos = pontos.filter(filtro_pontos)
            pratos = pratos.filter(filtro_pratos)
        else:
            # Sem termos relevantes na pergunta: usar os pontos turísticos
            # mais bem avaliados como contexto geral.
            provincias = provincias.none()
            pontos = pontos.order_by('-media_avaliacao')
            pratos = pratos.none()

        provincias = provincias[:self.LIMITE_RESULTADOS]
        pontos = pontos[:self.LIMITE_RESULTADOS]
        pratos = pratos[:self.LIMITE_RESULTADOS]

        return {
            'provincias': [
                {
                    'nome': p.nome,
                    'capital': p.capital,
                    'introducao': p.introducao,
                    'patrimonio': p.patrimonio,
                    'gastronomia': p.gastronomia,
                }
                for p in provincias
            ],
            'pontos_turisticos': [
                {
                    'nome': pt.nome,
                    'provincia': pt.provincia.nome,
                    'descricao': pt.descricao,
                    'preco_entrada': str(pt.preco_entrada) if pt.preco_entrada else None,
                    'entrada_gratuita': pt.entrada_gratuita,
                    'media_avaliacao': str(pt.media_avaliacao),
                }
                for pt in pontos
            ],
            'pratos_tipicos': [
                {
                    'nome': pr.nome,
                    'provincia': pr.provincia.nome,
                    'descricao': pr.descricao,
                    'faixa_preco': pr.faixa_preco,
                }
                for pr in pratos
            ],
        }

    # --------------------------------------------------------
    # Chamada ao modelo de IA
    # --------------------------------------------------------
    def _consultar_ia(self, pergunta, contexto_bd):
        """
        Chama a API da Anthropic com o contexto da base de dados embutido
        no prompt de sistema, para que a IA responda apenas com base em
        dados reais da plataforma Explora Angola.

        Requer `ANTHROPIC_API_KEY` definida em settings / variável de
        ambiente, e a dependência `pip install anthropic`.
        """
        if anthropic is None:
            raise RuntimeError('A biblioteca "anthropic" não está instalada (pip install anthropic).')

        cliente = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        prompt_sistema = (
            'És o Assistente IA da plataforma Explora Angola, especialista em '
            'turismo regional angolano. Respondes sempre em português, de forma '
            'simpática, objetiva e útil.\n\n'
            'Usa apenas a informação fornecida em "DADOS DISPONÍVEIS" abaixo, '
            'retirada diretamente da base de dados da plataforma. Se os dados '
            'não forem suficientes para responder com confiança, diz isso '
            'claramente e sugere ao utilizador explorar as páginas de '
            'Províncias, Pontos Turísticos ou Gastronomia. Nunca inventes '
            'preços, localizações ou nomes que não estejam nos dados.\n\n'
            f'DADOS DISPONÍVEIS:\n{json.dumps(contexto_bd, ensure_ascii=False, indent=2)}'
        )

        resposta = cliente.messages.create(
            model='claude-sonnet-4-6',
            max_tokens=700,
            system=prompt_sistema,
            messages=[{'role': 'user', 'content': pergunta}],
        )

        return ''.join(
            bloco.text for bloco in resposta.content if bloco.type == 'text'
        ).strip()


# ============================================================
# urls.py (apps/provincias) — acrescentar a "urlpatterns":
# ============================================================
#
# from .views import AssistenteIAView, AssistenteIAPerguntarView
#
# urlpatterns += [
#     path('assistente-ia/', AssistenteIAView.as_view(), name='assistente_ia'),
#     path('assistente-ia/perguntar/', AssistenteIAPerguntarView.as_view(), name='assistente_ia_perguntar'),
# ]