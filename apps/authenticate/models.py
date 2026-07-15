"""
============================================================
EXPLORA REGIÃO AI — apps/core/models.py
Usuário customizado + modelos base abstratos
============================================================
"""

import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


# ============================================================
# ABSTRAÇÕES BASE
# ============================================================

class ModeloBase(models.Model):
    """
    Classe base para todos os modelos do sistema.
    Fornece campos de auditoria e UUID como identificador público.
    """
    id            = models.UUIDField(default=uuid.uuid4, editable=False, unique=True,primary_key=True, db_index=True)
    criado_em     = models.DateTimeField(auto_now_add=True, verbose_name=_('Criado em'))
    atualizado_em = models.DateTimeField(auto_now=True,     verbose_name=_('Atualizado em'))
    ativo         = models.BooleanField(default=True,       verbose_name=_('Ativo'))

    class Meta:
        abstract = True
        ordering = ['-criado_em']


class ModeloPublicavel(ModeloBase):
    """
    Extensão de ModeloBase para conteúdo publicável.
    Suporta rascunho, publicado, arquivado.
    """

    class Status(models.TextChoices):
        RASCUNHO  = 'rascunho',  _('Rascunho')
        PUBLICADO = 'publicado', _('Publicado')
        ARQUIVADO = 'arquivado', _('Arquivado')

    status        = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.RASCUNHO,
        verbose_name=_('Status'),
        db_index=True,
    )
    publicado_em  = models.DateTimeField(null=True, blank=True, verbose_name=_('Publicado em'))
    destaque      = models.BooleanField(default=False, verbose_name=_('Em destaque'))
    ordem         = models.PositiveSmallIntegerField(default=0, verbose_name=_('Ordem de exibição'))

    class Meta:
        abstract = True

    def publicar(self):
        self.status = self.Status.PUBLICADO
        self.publicado_em = timezone.now()
        self.save(update_fields=['status', 'publicado_em'])

    def arquivar(self):
        self.status = self.Status.ARQUIVADO
        self.save(update_fields=['status'])


# ============================================================
# MANAGER DO USUÁRIO
# ============================================================

class UsuarioManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('O e-mail é obrigatório.'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)


# ============================================================
# USUÁRIO CUSTOMIZADO
# ============================================================

class Usuario(AbstractBaseUser, PermissionsMixin):
    """
    Usuário central do sistema.
    Suporta visitantes, empresas, guias, administradores.
    """

    class TipoUsuario(models.TextChoices):
        VISITANTE      = 'visitante',      _('Visitante')
        EMPRESA        = 'empresa',        _('Empresa Turística')
        GUIA           = 'guia',           _('Guia Turístico')
        GESTOR_LOCAL   = 'gestor_local',   _('Gestor Local')
        ADMINISTRADOR  = 'administrador',  _('Administrador')

    class Idioma(models.TextChoices):
        PT = 'pt', _('Português')
        EN = 'en', _('English')
        FR = 'fr', _('Français')
        ES = 'es', _('Español')

    # Identificação
    uuid        = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    email       = models.EmailField(unique=True, verbose_name=_('E-mail'))
    nome        = models.CharField(max_length=100, verbose_name=_('Nome'))
    apelido     = models.CharField(max_length=100, blank=True, verbose_name=_('Apelido'))
    foto_perfil = models.ImageField(
        upload_to='usuarios/fotos/%Y/%m/',
        null=True, blank=True,
        verbose_name=_('Foto de perfil'),
    )

    # Tipo e permissões
    tipo_usuario = models.CharField(
        max_length=20,
        choices=TipoUsuario.choices,
        default=TipoUsuario.VISITANTE,
        verbose_name=_('Tipo de usuário'),
        db_index=True,
    )
    is_staff     = models.BooleanField(default=False)
    is_active    = models.BooleanField(default=True)

    # Contacto
    telefone    = models.CharField(max_length=20, blank=True, verbose_name=_('Telefone'))
    bio         = models.TextField(blank=True, verbose_name=_('Biografia'))

    # Preferências
    idioma_preferido = models.CharField(
        max_length=5,
        choices=Idioma.choices,
        default=Idioma.PT,
        verbose_name=_('Idioma preferido'),
    )
    notificacoes_email = models.BooleanField(default=True,  verbose_name=_('Notificações por e-mail'))
    modo_escuro        = models.BooleanField(default=False, verbose_name=_('Modo escuro'))

    # Auditoria
    criado_em         = models.DateTimeField(auto_now_add=True)
    atualizado_em     = models.DateTimeField(auto_now=True)
    ultimo_acesso_em  = models.DateTimeField(null=True, blank=True)
    ip_ultimo_acesso  = models.GenericIPAddressField(null=True, blank=True)

    objects = UsuarioManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['nome']

    class Meta:
        db_table            = 'core_usuario'
        verbose_name        = _('Usuário')
        verbose_name_plural = _('Usuários')
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['tipo_usuario']),
        ]

    def __str__(self):
        return f'{self.nome} ({self.email})'

    @property
    def nome_completo(self):
        return f'{self.nome} {self.apelido}'.strip()


# ============================================================
# LOG DE ATIVIDADES DO SISTEMA
# ============================================================

class LogAtividade(models.Model):
    """
    Registo detalhado de ações realizadas no sistema.
    """

    class Acao(models.TextChoices):
        CRIACAO    = 'criacao',    _('Criação')
        EDICAO     = 'edicao',     _('Edição')
        REMOCAO    = 'remocao',    _('Remoção')
        LOGIN      = 'login',      _('Login')
        LOGOUT     = 'logout',     _('Logout')
        VISUALIZOU = 'visualizou', _('Visualizou')
        PESQUISOU  = 'pesquisou',  _('Pesquisou')
        EXPORTOU   = 'exportou',   _('Exportou')

    usuario        = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='logs_atividade',
    )
    acao           = models.CharField(max_length=20, choices=Acao.choices, db_index=True)
    descricao      = models.TextField()
    modelo_afetado = models.CharField(max_length=100, blank=True)
    objeto_id      = models.CharField(max_length=50, blank=True)
    ip_origem      = models.GenericIPAddressField(null=True, blank=True)
    agente_usuario = models.TextField(blank=True, verbose_name=_('User Agent'))
    dados_extras   = models.JSONField(default=dict, blank=True)
    criado_em      = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table            = 'core_log_atividade'
        verbose_name        = _('Log de Atividade')
        verbose_name_plural = _('Logs de Atividade')
        ordering            = ['-criado_em']
        indexes = [
            models.Index(fields=['usuario', 'acao']),
            models.Index(fields=['modelo_afetado', 'objeto_id']),
            models.Index(fields=['criado_em']),
        ]

    def __str__(self):
        return f'{self.usuario} — {self.acao} — {self.criado_em}'


# ============================================================
# CONFIGURAÇÕES DO SISTEMA
# ============================================================

class ConfiguracaoSistema(models.Model):
    """
    Tabela de configurações globais (chave-valor).
    """
    chave       = models.CharField(max_length=100, unique=True, verbose_name=_('Chave'))
    valor       = models.TextField(verbose_name=_('Valor'))
    descricao   = models.TextField(blank=True, verbose_name=_('Descrição'))
    tipo        = models.CharField(
        max_length=20,
        choices=[
            ('texto',   _('Texto')),
            ('numero',  _('Número')),
            ('booleano',_('Booleano')),
            ('json',    _('JSON')),
        ],
        default='texto',
    )
    editavel    = models.BooleanField(default=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table            = 'core_configuracao_sistema'
        verbose_name        = _('Configuração do Sistema')
        verbose_name_plural = _('Configurações do Sistema')

    def __str__(self):
        return f'{self.chave} = {self.valor}'


# ============================================================
# NOTIFICAÇÕES
# ============================================================

class Notificacao(ModeloBase):
    """
    Notificações internas para os usuários.
    """

    class Tipo(models.TextChoices):
        INFO     = 'info',     _('Informação')
        SUCESSO  = 'sucesso',  _('Sucesso')
        AVISO    = 'aviso',    _('Aviso')
        ERRO     = 'erro',     _('Erro')
        SISTEMA  = 'sistema',  _('Sistema')

    destinatario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='notificacoes',
    )
    tipo         = models.CharField(max_length=20, choices=Tipo.choices, default=Tipo.INFO)
    titulo       = models.CharField(max_length=200, verbose_name=_('Título'))
    mensagem     = models.TextField(verbose_name=_('Mensagem'))
    lida         = models.BooleanField(default=False, verbose_name=_('Lida'))
    lida_em      = models.DateTimeField(null=True, blank=True)
    url_destino  = models.URLField(blank=True, verbose_name=_('Link de destino'))

    class Meta:
        db_table            = 'core_notificacao'
        verbose_name        = _('Notificação')
        verbose_name_plural = _('Notificações')
        indexes = [
            models.Index(fields=['destinatario', 'lida']),
        ]

    def __str__(self):
        return f'{self.titulo} → {self.destinatario}'


# ============================================================
# MEDIA GENÉRICA (Imagens e Vídeos reutilizáveis)
# ============================================================

class Midia(ModeloBase):
    """
    Ficheiros de media (imagens, vídeos) reutilizáveis por qualquer entidade.
    """

    class TipoMidia(models.TextChoices):
        IMAGEM = 'imagem', _('Imagem')
        VIDEO  = 'video',  _('Vídeo')

    tipo        = models.CharField(max_length=10, choices=TipoMidia.choices, default=TipoMidia.IMAGEM)
    titulo      = models.CharField(max_length=200, blank=True)
    descricao   = models.TextField(blank=True)
    ficheiro    = models.FileField(upload_to='midia/%Y/%m/')
    url_externa = models.URLField(blank=True, verbose_name=_('URL externa (YouTube, Vimeo...)'))
    tamanho_kb  = models.PositiveIntegerField(null=True, blank=True)
    largura_px  = models.PositiveSmallIntegerField(null=True, blank=True)
    altura_px   = models.PositiveSmallIntegerField(null=True, blank=True)
    criado_por  = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='midias_criadas',
    )

    class Meta:
        db_table            = 'core_midia'
        verbose_name        = _('Média')
        verbose_name_plural = _('Mídias')

    def __str__(self):
        return self.titulo or self.ficheiro.name