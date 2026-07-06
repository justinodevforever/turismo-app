# from django.contrib import admin
# from django.utils.html import format_html

# from .models import (
#     Regiao,
#     Provincia,
#     Municipio,
#     CategoriaTurismo,
#     PontoTuristico,
#     PratoTipico,
#     Favorito,
#     ConversaAI,
# )


# # ==========================================================
# # REGIÃO
# # ==========================================================

# @admin.register(Regiao)
# class RegiaoAdmin(admin.ModelAdmin):
#     list_display = (
#         "nome",
#         "slug",
#         "status",
#         "publicado_em",
#     )

#     search_fields = (
#         "nome",
#         "descricao",
#     )

#     list_filter = (
#         "status",
#         "publicado_em",
#     )

#     prepopulated_fields = {
#         "slug": ("nome",)
#     }


# # ==========================================================
# # PROVÍNCIA
# # ==========================================================

# @admin.register(Provincia)
# class ProvinciaAdmin(admin.ModelAdmin):

#     list_display = (
#         "nome",
#         "regiao",
#         "capital",
#         "codigo_iso",
#         "populacao",
#         "status",
#     )

#     list_filter = (
#         "regiao",
#         "status",
#     )

#     search_fields = (
#         "nome",
#         "capital",
#         "codigo_iso",
#         "historia",
#         "cultura",
#     )

#     autocomplete_fields = (
#         "regiao",
#     )

#     filter_horizontal = (
#         "midias",
#     )

#     prepopulated_fields = {
#         "slug": ("nome",)
#     }


# # ==========================================================
# # MUNICÍPIO
# # ==========================================================

# @admin.register(Municipio)
# class MunicipioAdmin(admin.ModelAdmin):

#     list_display = (
#         "nome",
#         "provincia",
#         "populacao",
#         "status",
#     )

#     list_filter = (
#         "provincia",
#         "status",
#     )

#     search_fields = (
#         "nome",
#         "descricao",
#         "provincia__nome",
#     )

#     autocomplete_fields = (
#         "provincia",
#     )

#     prepopulated_fields = {
#         "slug": ("nome",)
#     }


# # ==========================================================
# # CATEGORIA
# # ==========================================================

# @admin.register(CategoriaTurismo)
# class CategoriaTurismoAdmin(admin.ModelAdmin):

#     list_display = (
#         "nome",
#         "icone",
#         "cor_hex",
#     )

#     search_fields = (
#         "nome",
#         "descricao",
#     )

#     prepopulated_fields = {
#         "slug": ("nome",)
#     }


# # ==========================================================
# # PONTO TURÍSTICO
# # ==========================================================

# @admin.register(PontoTuristico)
# class PontoTuristicoAdmin(admin.ModelAdmin):

#     list_display = (
#         "nome",
#         "provincia",
#         "municipio",
#         "media_avaliacao",
#         "status",
#     )

#     list_filter = (
#         "provincia",
#         "municipio",
#         "status",
#         "entrada_gratuita",
#     )

#     search_fields = (
#         "nome",
#         "descricao",
#         "provincia__nome",
#         "municipio__nome",
#     )

#     autocomplete_fields = (
#         "provincia",
#         "municipio",
#     )

#     filter_horizontal = (
#         "categorias",
#         "midias",
#     )

#     prepopulated_fields = {
#         "slug": ("nome",)
#     }


# # ==========================================================
# # PRATOS
# # ==========================================================

# @admin.register(PratoTipico)
# class PratoTipicoAdmin(admin.ModelAdmin):

#     list_display = (
#         "nome",
#         "provincia",
#         "vegetariano",
#         "destaque",
#     )

#     list_filter = (
#         "provincia",
#         "vegetariano",
#         "destaque",
#     )

#     search_fields = (
#         "nome",
#         "descricao",
#         "ingredientes",
#     )

#     autocomplete_fields = (
#         "provincia",
#     )

#     prepopulated_fields = {
#         "slug": ("nome",)
#     }


# # ==========================================================
# # FAVORITOS
# # ==========================================================

# @admin.register(Favorito)
# class FavoritoAdmin(admin.ModelAdmin):

#     list_display = (
#         "usuario",
#         "ponto_turistico",
#     )

#     search_fields = (
#         "usuario__nome_completo",
#         "usuario__email",
#         "ponto_turistico__nome",
#     )

#     autocomplete_fields = (
#         "usuario",
#         "ponto_turistico",
#     )


# # ==========================================================
# # CONVERSAS IA
# # ==========================================================

# @admin.register(ConversaAI)
# class ConversaAIAdmin(admin.ModelAdmin):

#     list_display = (
#         "usuario",
#         "criado_em",
#     )

#     search_fields = (
#         "usuario__nome_completo",
#         "usuario__email",
#         "pergunta",
#         "resposta",
#     )

#     autocomplete_fields = (
#         "usuario",
#     )

#     readonly_fields = (
#         "contexto",
#     )