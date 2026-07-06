"""
============================================================
EXPLORA REGIÃO AI — apps/core/admin.py
Django Admin personalizado para os modelos de core/models.py
============================================================

Objetivo: tornar o admin agradável e rápido de operar no dia-a-dia:
- Usuario com gestão de password correta (herda UserAdmin)
- Preview de imagens (foto_perfil, Midia)
- Ações em massa (ativar/inativar, publicar/arquivar, marcar lida)
- Filtros e pesquisa nos campos certos
- LogAtividade só de leitura (é um registo de auditoria)
- Mixins reutilizáveis para ModeloBase / ModeloPublicavel, para usar
  noutros apps que herdem desses modelos abstratos
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import (
    Usuario,
    LogAtividade,
    ConfiguracaoSistema,
    Notificacao,
    Midia,
)


# ============================================================
# MIXINS REUTILIZÁVEIS
# ============================================================
# Estes mixins não registam nada sozinhos — servem para os admins
# de OUTROS apps (ex.: Destino, Evento, Passeio...) que herdam de
# ModeloBase / ModeloPublicavel, evitando repetir código.

class ModeloBaseAdminMixin(admin.ModelAdmin):
    """Mixin para qualquer ModelAdmin de um modelo que herda ModeloBase."""

    readonly_fields = ('uuid', 'criado_em', 'atualizado_em')
    list_filter = ('ativo',)
    actions = ['acao_ativar', 'acao_inativar']

    @admin.action(description=_('✅ Ativar selecionados'))
    def acao_ativar(self, request, queryset):
        atualizados = queryset.update(ativo=True)
        self.message_user(request, _(f'{atualizados} registo(s) ativado(s).'))

    @admin.action(description=_('🚫 Inativar selecionados'))
    def acao_inativar(self, request, queryset):
        atualizados = queryset.update(ativo=False)
        self.message_user(request, _(f'{atualizados} registo(s) inativado(s).'))


class ModeloPublicavelAdminMixin(ModeloBaseAdminMixin):
    """Mixin para qualquer ModelAdmin de um modelo que herda ModeloPublicavel."""

    list_filter = ModeloBaseAdminMixin.list_filter + ('status', 'destaque')
    actions = ModeloBaseAdminMixin.actions + ['acao_publicar', 'acao_arquivar']

    @admin.action(description=_('📢 Publicar selecionados'))
    def acao_publicar(self, request, queryset):
        for obj in queryset:
            obj.publicar()
        self.message_user(request, _(f'{queryset.count()} registo(s) publicado(s).'))

    @admin.action(description=_('🗄️ Arquivar selecionados'))
    def acao_arquivar(self, request, queryset):
        for obj in queryset:
            obj.arquivar()
        self.message_user(request, _(f'{queryset.count()} registo(s) arquivado(s).'))


# ============================================================
# USUÁRIO
# ============================================================

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """
    Admin do usuário customizado.
    Herda de UserAdmin (e não de ModelAdmin puro) para manter o fluxo
    correto de criação/alteração de password com hashing.
    """

    model = Usuario
    ordering = ('-criado_em',)

    list_display = (
        'email', 'nome', 'apelido', 'tipo_usuario_badge',
        'foto_preview', 'is_active', 'is_staff', 'ultimo_acesso_em', 'criado_em',
    )
    list_display_links = ('email', 'nome')
    list_filter = ('tipo_usuario', 'is_active', 'is_staff', 'idioma_preferido', 'criado_em')
    search_fields = ('email', 'nome', 'apelido', 'telefone')
    readonly_fields = ('uuid', 'criado_em', 'atualizado_em', 'ultimo_acesso_em', 'ip_ultimo_acesso', 'foto_preview_grande')
    date_hierarchy = 'criado_em'
    list_per_page = 30

    # Sem 'username' — o login é feito por e-mail
    fieldsets = (
        (_('Credenciais'), {'fields': ('email', 'password')}),
        (_('Dados pessoais'), {
            'fields': ('nome', 'apelido', 'telefone', 'bio', 'foto_perfil', 'foto_preview_grande')
        }),
        (_('Tipo e permissões'), {
            'fields': ('tipo_usuario', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Preferências'), {
            'fields': ('idioma_preferido', 'notificacoes_email', 'modo_escuro')
        }),
        (_('Auditoria'), {
            'fields': ('uuid', 'criado_em', 'atualizado_em', 'ultimo_acesso_em', 'ip_ultimo_acesso'),
            'classes': ('collapse',),
        }),
    )

    add_fieldsets = (
        (_('Criar usuário'), {
            'classes': ('wide',),
            'fields': ('email', 'nome', 'tipo_usuario', 'password1', 'password2'),
        }),
    )

    actions = ['acao_ativar', 'acao_inativar']

    @admin.action(description=_('✅ Ativar contas selecionadas'))
    def acao_ativar(self, request, queryset):
        atualizados = queryset.update(is_active=True)
        self.message_user(request, _(f'{atualizados} conta(s) ativada(s).'))

    @admin.action(description=_('🚫 Inativar contas selecionadas'))
    def acao_inativar(self, request, queryset):
        atualizados = queryset.update(is_active=False)
        self.message_user(request, _(f'{atualizados} conta(s) inativada(s).'))

    @admin.display(description=_('Tipo'))
    def tipo_usuario_badge(self, obj):
        cores = {
            'visitante': '#6b7280',
            'empresa': '#2563eb',
            'guia': '#059669',
            'gestor_local': '#d97706',
            'administrador': '#dc2626',
        }
        cor = cores.get(obj.tipo_usuario, '#6b7280')
        return format_html(
            '<span style="background:{}; color:white; padding:2px 8px; '
            'border-radius:10px; font-size:11px;">{}</span>',
            cor, obj.get_tipo_usuario_display(),
        )

    @admin.display(description=_('Foto'))
    def foto_preview(self, obj):
        if obj.foto_perfil:
            return format_html(
                '<img src="{}" style="width:32px; height:32px; border-radius:50%; object-fit:cover;" />',
                obj.foto_perfil.url,
            )
        return '—'

    @admin.display(description=_('Pré-visualização'))
    def foto_preview_grande(self, obj):
        if obj.foto_perfil:
            return format_html(
                '<img src="{}" style="width:120px; height:120px; border-radius:8px; object-fit:cover;" />',
                obj.foto_perfil.url,
            )
        return _('Sem foto')


# ============================================================
# LOG DE ATIVIDADE (somente leitura — é um registo de auditoria)
# ============================================================

@admin.register(LogAtividade)
class LogAtividadeAdmin(admin.ModelAdmin):
    list_display = ('criado_em', 'usuario', 'acao_badge', 'modelo_afetado', 'objeto_id', 'ip_origem')
    list_filter = ('acao', 'modelo_afetado', 'criado_em')
    search_fields = ('usuario__email', 'usuario__nome', 'descricao', 'objeto_id', 'ip_origem')
    date_hierarchy = 'criado_em'
    list_select_related = ('usuario',)
    list_per_page = 50
    readonly_fields = [f.name for f in LogAtividade._meta.fields]  # tudo readonly

    def has_add_permission(self, request):
        return False  # logs são criados pelo sistema, não manualmente

    def has_change_permission(self, request, obj=None):
        return False  # logs não devem ser editados

    def has_delete_permission(self, request, obj=None):
        # permite apenas a superusuários limpar logs antigos, se necessário
        return request.user.is_superuser

    @admin.display(description=_('Ação'))
    def acao_badge(self, obj):
        cores = {
            'criacao': '#059669', 'edicao': '#2563eb', 'remocao': '#dc2626',
            'login': '#6b7280', 'logout': '#9ca3af', 'visualizou': '#6366f1',
            'pesquisou': '#8b5cf6', 'exportou': '#d97706',
        }
        cor = cores.get(obj.acao, '#6b7280')
        return format_html(
            '<span style="background:{}; color:white; padding:2px 8px; border-radius:10px; font-size:11px;">{}</span>',
            cor, obj.get_acao_display(),
        )


# ============================================================
# CONFIGURAÇÃO DO SISTEMA
# ============================================================

@admin.register(ConfiguracaoSistema)
class ConfiguracaoSistemaAdmin(admin.ModelAdmin):
    list_display = ('chave', 'valor_resumido', 'tipo', 'editavel', 'atualizado_em')
    list_filter = ('tipo', 'editavel')
    search_fields = ('chave', 'descricao')
    list_editable = ()  # 'valor' fica no form, não na lista, por segurança
    readonly_fields = ('atualizado_em',)

    fieldsets = (
        (None, {'fields': ('chave', 'valor', 'tipo', 'descricao', 'editavel')}),
        (_('Auditoria'), {'fields': ('atualizado_em',)}),
    )

    def get_readonly_fields(self, request, obj=None):
        # se a config estiver marcada como não-editável, bloqueia o campo 'valor'
        if obj and not obj.editavel:
            return self.readonly_fields + ('chave', 'valor', 'tipo')
        return self.readonly_fields

    @admin.display(description=_('Valor'))
    def valor_resumido(self, obj):
        texto = obj.valor or ''
        return texto if len(texto) <= 60 else texto[:57] + '...'


# ============================================================
# NOTIFICAÇÕES
# ============================================================

@admin.register(Notificacao)
class NotificacaoAdmin(ModeloBaseAdminMixin):
    list_display = ('titulo', 'destinatario', 'tipo_badge', 'lida', 'criado_em')
    list_filter = ModeloBaseAdminMixin.list_filter + ('tipo', 'lida')
    search_fields = ('titulo', 'mensagem', 'destinatario__email', 'destinatario__nome')
    list_select_related = ('destinatario',)
    date_hierarchy = 'criado_em'
    autocomplete_fields = ('destinatario',)

    actions = ModeloBaseAdminMixin.actions + ['acao_marcar_lida', 'acao_marcar_nao_lida']

    @admin.action(description=_('✔️ Marcar como lida'))
    def acao_marcar_lida(self, request, queryset):
        from django.utils import timezone
        atualizados = queryset.update(lida=True, lida_em=timezone.now())
        self.message_user(request, _(f'{atualizados} notificação(ões) marcada(s) como lida(s).'))

    @admin.action(description=_('↩️ Marcar como não lida'))
    def acao_marcar_nao_lida(self, request, queryset):
        atualizados = queryset.update(lida=False, lida_em=None)
        self.message_user(request, _(f'{atualizados} notificação(ões) marcada(s) como não lida(s).'))

    @admin.display(description=_('Tipo'))
    def tipo_badge(self, obj):
        cores = {
            'info': '#2563eb', 'sucesso': '#059669',
            'aviso': '#d97706', 'erro': '#dc2626', 'sistema': '#6b7280',
        }
        cor = cores.get(obj.tipo, '#6b7280')
        return format_html(
            '<span style="background:{}; color:white; padding:2px 8px; border-radius:10px; font-size:11px;">{}</span>',
            cor, obj.get_tipo_display(),
        )


# ============================================================
# MÍDIA
# ============================================================

@admin.register(Midia)
class MidiaAdmin(ModeloBaseAdminMixin):
    list_display = ('preview', 'titulo', 'tipo', 'criado_por', 'tamanho_kb', 'dimensoes', 'criado_em')
    list_filter = ModeloBaseAdminMixin.list_filter + ('tipo',)
    search_fields = ('titulo', 'descricao', 'ficheiro', 'url_externa')
    list_select_related = ('criado_por',)
    autocomplete_fields = ('criado_por',)
    readonly_fields = ModeloBaseAdminMixin.readonly_fields + ('preview_grande',)

    fieldsets = (
        (None, {'fields': ('tipo', 'titulo', 'descricao')}),
        (_('Ficheiro'), {'fields': ('ficheiro', 'preview_grande', 'url_externa')}),
        (_('Metadados'), {'fields': ('tamanho_kb', 'largura_px', 'altura_px', 'criado_por')}),
        (_('Auditoria'), {'fields': ('uuid', 'criado_em', 'atualizado_em', 'ativo'), 'classes': ('collapse',)}),
    )

    @admin.display(description=_('Preview'))
    def preview(self, obj):
        if obj.tipo == obj.TipoMidia.IMAGEM and obj.ficheiro:
            return format_html(
                '<img src="{}" style="width:40px; height:40px; object-fit:cover; border-radius:4px;" />',
                obj.ficheiro.url,
            )
        return '🎬' if obj.tipo == obj.TipoMidia.VIDEO else '—'

    @admin.display(description=_('Pré-visualização'))
    def preview_grande(self, obj):
        if obj.tipo == obj.TipoMidia.IMAGEM and obj.ficheiro:
            return format_html(
                '<img src="{}" style="max-width:300px; max-height:300px; border-radius:8px;" />',
                obj.ficheiro.url,
            )
        if obj.url_externa:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.url_externa, obj.url_externa)
        return _('Sem preview')

    @admin.display(description=_('Dimensões'))
    def dimensoes(self, obj):
        if obj.largura_px and obj.altura_px:
            return f'{obj.largura_px}×{obj.altura_px}px'
        return '—'


# ============================================================
# PERSONALIZAÇÃO GLOBAL DO SITE ADMIN
# ============================================================

admin.site.site_header = 'Explora Região AI — Administração'
admin.site.site_title = 'Explora Região AI'
admin.site.index_title = 'Painel de Gestão'