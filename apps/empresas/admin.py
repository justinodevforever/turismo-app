"""
============================================================
EXPLORA REGIÃO AI — apps/empresas/admin.py
Admin personalizado: Hotéis, Restaurantes, Guias e Serviços
============================================================
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.db.models import Count

from .models import (
    EmpresaTuristica,
    Hotel,
    TipoQuarto,
    Restaurante,
    ItemMenu,
    GuiaTuristico,
)


# ============================================================
# HELPERS / MIXINS
# ============================================================

class PreviewImagemMixin:
    """Mostra uma miniatura de qualquer ImageField no admin."""

    def _preview(self, campo_arquivo, altura=60):
        if campo_arquivo:
            return format_html(
                '<img src="{}" style="height:{}px;border-radius:6px;'
                'box-shadow:0 0 3px rgba(0,0,0,.3);" />',
                campo_arquivo.url, altura,
            )
        return "—"


# ============================================================
# AÇÕES EM MASSA (reutilizáveis)
# ============================================================

@admin.action(description=_("✅ Aprovar empresas selecionadas"))
def aprovar_empresas(modeladmin, request, queryset):
    atualizados = queryset.update(
        status_verificacao=EmpresaTuristica.StatusVerificacao.APROVADO,
        verificado_por=request.user,
    )
    modeladmin.message_user(request, f"{atualizados} empresa(s) aprovada(s).")


@admin.action(description=_("⛔ Rejeitar empresas selecionadas"))
def rejeitar_empresas(modeladmin, request, queryset):
    atualizados = queryset.update(
        status_verificacao=EmpresaTuristica.StatusVerificacao.REJEITADO,
        verificado_por=request.user,
    )
    modeladmin.message_user(request, f"{atualizados} empresa(s) rejeitada(s).", level="warning")


@admin.action(description=_("⏸ Suspender empresas selecionadas"))
def suspender_empresas(modeladmin, request, queryset):
    atualizados = queryset.update(status_verificacao=EmpresaTuristica.StatusVerificacao.SUSPENSO)
    modeladmin.message_user(request, f"{atualizados} empresa(s) suspensa(s).", level="warning")


@admin.action(description=_("⭐ Marcar como destaque"))
def marcar_destaque(modeladmin, request, queryset):
    atualizados = queryset.update(destaque=True)
    modeladmin.message_user(request, f"{atualizados} empresa(s) marcada(s) como destaque.")


# ============================================================
# INLINES
# ============================================================

class TipoQuartoInline(admin.TabularInline):
    model = TipoQuarto
    extra = 0
    fields = ("tipo", "nome", "capacidade", "preco_noite", "total_quartos", "foto")
    show_change_link = True


class ItemMenuInline(admin.TabularInline):
    model = ItemMenu
    extra = 0
    fields = ("categoria", "nome", "preco", "vegetariano", "vegano", "picante", "mais_pedido", "publicado_em")
    show_change_link = True


class HotelInline(admin.StackedInline):
    model = Hotel
    can_delete = False
    extra = 0
    fk_name = "empresa"
    fieldsets = (
        (None, {
            "fields": (
                "nome", "classificacao", "total_quartos",
                ("check_in_hora", "check_out_hora"),
                ("preco_min_noite", "preco_max_noite"),
                "foto",
            )
        }),
        (_("Comodidades"), {
            "classes": ("collapse",),
            "fields": (
                ("tem_wifi", "tem_piscina", "tem_estacionamento", "tem_academia"),
                ("tem_spa", "tem_restaurante", "tem_bar", "tem_ar_condicionado"),
                ("aceita_animais", "servico_quarto"),
            ),
        }),
        (_("Políticas"), {
            "classes": ("collapse",),
            "fields": ("politica_cancelamento", "regras_casa"),
        }),
    )


class RestauranteInline(admin.StackedInline):
    model = Restaurante
    can_delete = False
    extra = 0
    fk_name = "empresa"
    fieldsets = (
        (None, {
            "fields": (
                "nome", "tipo_cozinha", "capacidade",
                ("preco_medio", "faixa_preco"),
                "foto",
            )
        }),
        (_("Serviços"), {
            "classes": ("collapse",),
            "fields": (
                ("tem_entrega", "tem_takeaway", "reserva_obrigatoria"),
                ("aceita_cartao", "tem_wifi"),
            ),
        }),
        (_("Detalhes"), {
            "classes": ("collapse",),
            "fields": ("especialidades", "endereco"),
        }),
    )


class GuiaInline(admin.StackedInline):
    model = GuiaTuristico
    can_delete = False
    extra = 0
    fk_name = "empresa"
    autocomplete_fields = ("usuario",)
    filter_horizontal = ("provincias_atuacao",)
    fields = (
        "usuario", "nivel_experiencia", "anos_experiencia",
        "numero_licenca", "certificado", "foto",
        "idiomas", "especializacoes", "provincias_atuacao",
        ("preco_hora", "preco_dia_completo"), "disponivel",
    )


# ============================================================
# EMPRESA TURÍSTICA (ADMIN PRINCIPAL / HUB)
# ============================================================

@admin.register(EmpresaTuristica)
class EmpresaTuristicaAdmin(PreviewImagemMixin, admin.ModelAdmin):
    list_display = (
        "logo_preview", "nome", "tipo_empresa_badge", "provincia",
        "municipio", "status_badge", "media_avaliacao", "total_avaliacoes",
        "destaque", "criado_em",
    )
    list_display_links = ("nome",)
    list_filter = (
        "tipo_empresa", "status_verificacao", "provincia",
        "destaque", "publicado_em",
    )
    search_fields = (
        "nome", "descricao", "email", "telefone", "whatsapp",
        "proprietario__nome_completo", "proprietario__email",
    )
    prepopulated_fields = {"slug": ("nome",)}
    autocomplete_fields = ("proprietario", "provincia", "municipio")
    readonly_fields = (
        "media_avaliacao", "total_avaliacoes", "total_visualizacoes",
        "verificado_por", "verificado_em", "logo_preview_grande", "capa_preview",
    )
    list_per_page = 25
    date_hierarchy = "criado_em"
    save_on_top = True
    actions = [aprovar_empresas, rejeitar_empresas, suspender_empresas, marcar_destaque]

    fieldsets = (
        (_("Identificação"), {
            "fields": (
                "proprietario", "tipo_empresa", "nome", "slug",
                "slogan", "descricao",
            )
        }),
        (_("Verificação"), {
            "fields": (
                "status_verificacao", "verificado_por", "verificado_em",
                "motivo_rejeicao",
            )
        }),
        (_("Localização"), {
            "fields": (
                "provincia", "municipio", "bairro", "endereco",
                ("latitude", "longitude"),
            )
        }),
        (_("Contacto"), {
            "classes": ("collapse",),
            "fields": (
                ("telefone", "telefone_alt"), "email", "whatsapp",
                "website", "instagram", "facebook",
            )
        }),
        (_("Mídia"), {
            "fields": ("logo", "logo_preview_grande", "foto_capa", "capa_preview", "midias"),
        }),
        (_("Horário"), {
            "classes": ("collapse",),
            "fields": ("horario_funcionamento",),
        }),
        (_("Métricas"), {
            "classes": ("collapse",),
            "fields": ("media_avaliacao", "total_avaliacoes", "total_visualizacoes"),
        }),
        (_("SEO"), {
            "classes": ("collapse",),
            "fields": ("meta_titulo", "meta_descricao"),
        }),
        (_("Publicação"), {
            "fields": ("publicado_em", "destaque"),
        }),
    )

    filter_horizontal = ("midias",)

    def get_inlines(self, request, obj):
        """Mostra o inline certo consoante o tipo de empresa já gravada."""
        if obj is None:
            return []
        mapa = {
            EmpresaTuristica.TipoEmpresa.HOTEL: [HotelInline],
            EmpresaTuristica.TipoEmpresa.RESTAURANTE: [RestauranteInline],
            EmpresaTuristica.TipoEmpresa.GUIA: [GuiaInline],
        }
        return mapa.get(obj.tipo_empresa, [])

    @admin.display(description=_("Logo"))
    def logo_preview(self, obj):
        return self._preview(obj.logo, altura=36)

    @admin.display(description=_("Logo"))
    def logo_preview_grande(self, obj):
        return self._preview(obj.logo, altura=150)

    @admin.display(description=_("Capa"))
    def capa_preview(self, obj):
        return self._preview(obj.foto_capa, altura=150)

    @admin.display(description=_("Tipo"), ordering="tipo_empresa")
    def tipo_empresa_badge(self, obj):
        cores = {
            "hotel": "#2563eb", "restaurante": "#d97706", "guia": "#16a34a",
            "agencia": "#7c3aed", "transporte": "#0891b2", "artesanato": "#be123c",
            "outro": "#6b7280",
        }
        cor = cores.get(obj.tipo_empresa, "#6b7280")
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:10px;font-size:11px;">{}</span>',
            cor, obj.get_tipo_empresa_display(),
        )

    @admin.display(description=_("Estado"), ordering="status_verificacao")
    def status_badge(self, obj):
        cores = {
            "pendente": "#f59e0b", "aprovado": "#16a34a",
            "rejeitado": "#dc2626", "suspenso": "#6b7280",
        }
        cor = cores.get(obj.status_verificacao, "#6b7280")
        return format_html(
            '<b style="color:{};">● {}</b>', cor, obj.get_status_verificacao_display(),
        )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "proprietario", "provincia", "municipio", "verificado_por"
        )


# ============================================================
# HOTEL (gestão independente, além do inline)
# ============================================================

@admin.register(Hotel)
class HotelAdmin(PreviewImagemMixin, admin.ModelAdmin):
    list_display = (
        "foto_preview", "empresa", "classificacao_estrelas", "total_quartos",
        "faixa_precos", "tem_wifi", "tem_piscina", "aceita_animais",
    )
    list_filter = (
        "classificacao", "tem_wifi", "tem_piscina", "tem_estacionamento",
        "tem_spa", "aceita_animais", "empresa__provincia",
    )
    search_fields = ("empresa__nome", "nome")
    autocomplete_fields = ("empresa",)
    inlines = [TipoQuartoInline]
    readonly_fields = ("foto_preview_grande",)
    list_per_page = 25

    fieldsets = (
        (None, {"fields": ("empresa", "nome", "classificacao", "total_quartos")}),
        (_("Horários e preços"), {
            "fields": (("check_in_hora", "check_out_hora"), ("preco_min_noite", "preco_max_noite"))
        }),
        (_("Comodidades"), {
            "fields": (
                ("tem_wifi", "tem_piscina", "tem_estacionamento", "tem_academia"),
                ("tem_spa", "tem_restaurante", "tem_bar", "tem_ar_condicionado"),
                ("aceita_animais", "servico_quarto"),
            )
        }),
        (_("Políticas"), {"classes": ("collapse",), "fields": ("politica_cancelamento", "regras_casa")}),
        (_("Foto"), {"fields": ("foto", "foto_preview_grande")}),
    )

    @admin.display(description=_("Foto"))
    def foto_preview(self, obj):
        return self._preview(obj.foto, altura=36)

    @admin.display(description=_("Foto"))
    def foto_preview_grande(self, obj):
        return self._preview(obj.foto, altura=150)

    @admin.display(description=_("Estrelas"), ordering="classificacao")
    def classificacao_estrelas(self, obj):
        if obj.classificacao:
            return "★" * int(obj.classificacao)
        return "—"

    @admin.display(description=_("Preço/noite (AOA)"))
    def faixa_precos(self, obj):
        if obj.preco_min_noite and obj.preco_max_noite:
            return f"{obj.preco_min_noite:,.0f} – {obj.preco_max_noite:,.0f}"
        return "—"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("empresa").annotate(
            n_tipos_quarto=Count("tipos_quarto")
        )


@admin.register(TipoQuarto)
class TipoQuartoAdmin(PreviewImagemMixin, admin.ModelAdmin):
    list_display = ("foto_preview", "hotel", "tipo", "nome", "capacidade", "preco_noite", "total_quartos")
    list_filter = ("tipo", "hotel__empresa__provincia")
    search_fields = ("nome", "hotel__empresa__nome")
    autocomplete_fields = ("hotel",)
    list_editable = ("preco_noite", "total_quartos")

    @admin.display(description=_("Foto"))
    def foto_preview(self, obj):
        return self._preview(obj.foto, altura=36)


# ============================================================
# RESTAURANTE
# ============================================================

@admin.register(Restaurante)
class RestauranteAdmin(PreviewImagemMixin, admin.ModelAdmin):
    list_display = (
        "foto_preview", "empresa", "tipo_cozinha", "faixa_preco",
        "capacidade", "preco_medio", "tem_entrega", "reserva_obrigatoria",
    )
    list_filter = (
        "tipo_cozinha", "faixa_preco", "tem_entrega", "tem_takeaway",
        "reserva_obrigatoria", "aceita_cartao", "empresa__provincia",
    )
    search_fields = ("empresa__nome", "nome", "especialidades")
    autocomplete_fields = ("empresa",)
    inlines = [ItemMenuInline]
    readonly_fields = ("foto_preview_grande",)
    list_per_page = 25

    fieldsets = (
        (None, {"fields": ("empresa", "nome", "tipo_cozinha", "capacidade")}),
        (_("Preços"), {"fields": (("preco_medio", "faixa_preco"),)}),
        (_("Serviços"), {
            "fields": (
                ("tem_entrega", "tem_takeaway", "reserva_obrigatoria"),
                ("aceita_cartao", "tem_wifi"),
            )
        }),
        (_("Detalhes"), {"fields": ("especialidades", "endereco")}),
        (_("Foto"), {"fields": ("foto", "foto_preview_grande")}),
    )

    @admin.display(description=_("Foto"))
    def foto_preview(self, obj):
        return self._preview(obj.foto, altura=36)

    @admin.display(description=_("Foto"))
    def foto_preview_grande(self, obj):
        return self._preview(obj.foto, altura=150)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("empresa").annotate(
            n_itens_menu=Count("menu")
        )


@admin.register(ItemMenu)
class ItemMenuAdmin(PreviewImagemMixin, admin.ModelAdmin):
    list_display = (
        "foto_preview", "nome", "restaurante", "categoria", "preco",
        "vegetariano", "vegano", "picante", "mais_pedido", "publicado_em",
    )
    list_filter = ("categoria", "vegetariano", "vegano", "sem_gluten", "picante", "mais_pedido", "publicado_em")
    search_fields = ("nome", "descricao", "ingredientes", "restaurante__empresa__nome")
    autocomplete_fields = ("restaurante",)
    list_editable = ("preco", "mais_pedido", "publicado_em")

    @admin.display(description=_("Foto"))
    def foto_preview(self, obj):
        return self._preview(obj.foto, altura=36)


# ============================================================
# GUIA TURÍSTICO
# ============================================================

@admin.register(GuiaTuristico)
class GuiaTuristicoAdmin(PreviewImagemMixin, admin.ModelAdmin):
    list_display = (
        "foto_preview", "usuario", "nivel_experiencia", "anos_experiencia",
        "numero_licenca", "disponivel_badge", "preco_hora", "preco_dia_completo",
        "media_avaliacao", "total_excursoes",
    )
    list_filter = ("nivel_experiencia", "disponivel", "provincias_atuacao")
    search_fields = (
        "usuario__nome_completo", "usuario__email", "numero_licenca",
        "empresa__nome",
    )
    autocomplete_fields = ("usuario", "empresa")
    filter_horizontal = ("provincias_atuacao",)
    readonly_fields = (
        "total_excursoes", "media_avaliacao", "total_avaliacoes", "foto_preview_grande",
    )
    list_editable = ("preco_hora", "preco_dia_completo")
    list_per_page = 25

    fieldsets = (
        (None, {"fields": ("usuario", "empresa", "nivel_experiencia", "anos_experiencia")}),
        (_("Licença e certificação"), {"fields": ("numero_licenca", "certificado", "foto", "foto_preview_grande")}),
        (_("Áreas de atuação"), {"fields": ("provincias_atuacao", "idiomas", "especializacoes")}),
        (_("Tarifas e disponibilidade"), {"fields": (("preco_hora", "preco_dia_completo"), "disponivel")}),
        (_("Métricas"), {
            "classes": ("collapse",),
            "fields": ("total_excursoes", "media_avaliacao", "total_avaliacoes"),
        }),
    )

    @admin.display(description=_("Foto"))
    def foto_preview(self, obj):
        return self._preview(obj.foto, altura=36)

    @admin.display(description=_("Foto"))
    def foto_preview_grande(self, obj):
        return self._preview(obj.foto, altura=150)

    @admin.display(description=_("Disponível"), ordering="disponivel", boolean=False)
    def disponivel_badge(self, obj):
        cor = "#16a34a" if obj.disponivel else "#dc2626"
        texto = "Disponível" if obj.disponivel else "Indisponível"
        return format_html('<b style="color:{};">● {}</b>', cor, texto)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("usuario", "empresa")