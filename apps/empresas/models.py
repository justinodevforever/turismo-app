"""
============================================================
EXPLORA REGIÃO AI — apps/empresas/models.py
Hotéis, Restaurantes, Guias Turísticos e Serviços
============================================================
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

from apps.authenticate.models import ModeloBase, ModeloPublicavel, Usuario, Midia
from apps.provincias.models import Provincia, Municipio


# ============================================================
# EMPRESA TURÍSTICA (BASE)
# ============================================================

class EmpresaTuristica(ModeloPublicavel):
    """
    Entidade base para qualquer negócio turístico registado.
    Hotéis, restaurantes e guias herdam desta base.
    """

    class TipoEmpresa(models.TextChoices):
        HOTEL       = 'hotel',       _('Hotel / Alojamento')
        RESTAURANTE = 'restaurante', _('Restaurante')
        GUIA        = 'guia',        _('Guia Turístico')
        AGENCIA     = 'agencia',     _('Agência de Viagens')
        TRANSPORTE  = 'transporte',  _('Transporte')
        ARTESANATO  = 'artesanato',  _('Artesanato / Loja')
        OUTRO       = 'outro',       _('Outro')

    class StatusVerificacao(models.TextChoices):
        PENDENTE  = 'pendente',  _('Pendente de verificação')
        APROVADO  = 'aprovado',  _('Aprovado')
        REJEITADO = 'rejeitado', _('Rejeitado')
        SUSPENSO  = 'suspenso',  _('Suspenso')

    # Identificação
    proprietario    = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='empresas_registadas',
        verbose_name=_('Proprietário'),
    )
    tipo_empresa    = models.CharField(
        max_length=20,
        choices=TipoEmpresa.choices,
        default=TipoEmpresa.OUTRO,
        db_index=True,
    )
    nome            = models.CharField(max_length=200, verbose_name=_('Nome'))
    slug            = models.SlugField(max_length=220, unique=True)
    descricao       = models.TextField(verbose_name=_('Descrição'))
    slogan          = models.CharField(max_length=200, blank=True)

    # Verificação
    status_verificacao = models.CharField(
        max_length=20,
        choices=StatusVerificacao.choices,
        default=StatusVerificacao.PENDENTE,
        db_index=True,
    )
    verificado_por  = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='empresas_verificadas',
    )
    verificado_em   = models.DateTimeField(null=True, blank=True)
    motivo_rejeicao = models.TextField(blank=True)

    # Localização
    provincia   = models.ForeignKey(
        Provincia,
        on_delete=models.PROTECT,
        related_name='empresas',
        verbose_name=_('Província'),
    )
    municipio   = models.ForeignKey(
        Municipio,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='empresas',
    )
    endereco        = models.CharField(max_length=300, blank=True)
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    bairro          = models.CharField(max_length=100, blank=True)

    # Contacto
    telefone        = models.CharField(max_length=20, blank=True)
    telefone_alt    = models.CharField(max_length=20, blank=True)
    email           = models.EmailField(blank=True)
    website         = models.URLField(blank=True)
    instagram       = models.URLField(blank=True)
    facebook        = models.URLField(blank=True)
    whatsapp        = models.CharField(max_length=20, blank=True)

    # Mídia
    logo            = models.ImageField(upload_to='empresas/logos/', null=True, blank=True)
    foto_capa       = models.ImageField(upload_to='empresas/capas/%Y/', null=True, blank=True)
    midias          = models.ManyToManyField(Midia, blank=True, related_name='empresas')

    # Horário
    horario_funcionamento = models.JSONField(
        default=dict, blank=True,
        help_text=_('Ex.: {"seg":"08:00-18:00","dom":"fechado"}'),
    )

    # Métricas
    media_avaliacao     = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_avaliacoes    = models.PositiveIntegerField(default=0)
    total_visualizacoes = models.PositiveIntegerField(default=0)

    # SEO
    meta_titulo    = models.CharField(max_length=70, blank=True)
    meta_descricao = models.CharField(max_length=160, blank=True)

    class Meta:
        db_table            = 'empresas_empresa_turistica'
        verbose_name        = _('Empresa Turística')
        verbose_name_plural = _('Empresas Turísticas')
        ordering            = ['-destaque', 'nome']
        indexes = [
            models.Index(fields=['tipo_empresa', 'status_verificacao']),
            models.Index(fields=['provincia', 'tipo_empresa']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return f'{self.nome} ({self.get_tipo_empresa_display()})'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)


# ============================================================
# HOTEL / ALOJAMENTO
# ============================================================

class Hotel(ModeloBase):
    """
    Dados específicos de Hotéis e Alojamentos.
    """

    class Classificacao(models.TextChoices):
        ESTRELA_1 = '1', _('1 Estrela')
        ESTRELA_2 = '2', _('2 Estrelas')
        ESTRELA_3 = '3', _('3 Estrelas')
        ESTRELA_4 = '4', _('4 Estrelas')
        ESTRELA_5 = '5', _('5 Estrelas')

    empresa         = models.OneToOneField(
        EmpresaTuristica,
        on_delete=models.CASCADE,
        related_name='hotel',
        limit_choices_to={'tipo_empresa': 'hotel'},
    )
    nome = models.CharField(max_length=200, blank=True, null=True)
    classificacao   = models.CharField(
        max_length=1,
        choices=Classificacao.choices,
        null=True, blank=True,
        verbose_name=_('Classificação em estrelas'),
    )
    total_quartos   = models.PositiveSmallIntegerField(default=0, verbose_name=_('Total de quartos'))
    check_in_hora   = models.TimeField(null=True, blank=True, verbose_name=_('Hora de check-in'))
    check_out_hora  = models.TimeField(null=True, blank=True, verbose_name=_('Hora de check-out'))
    preco_min_noite = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_('Preço mínimo/noite (AOA)'))
    preco_max_noite = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_('Preço máximo/noite (AOA)'))

    # Comodidades (flags booleanas)
    tem_wifi         = models.BooleanField(default=False, verbose_name=_('Wi-Fi'))
    tem_piscina      = models.BooleanField(default=False, verbose_name=_('Piscina'))
    tem_estacionamento = models.BooleanField(default=False, verbose_name=_('Estacionamento'))
    tem_academia     = models.BooleanField(default=False, verbose_name=_('Academia'))
    tem_spa          = models.BooleanField(default=False, verbose_name=_('Spa'))
    tem_restaurante  = models.BooleanField(default=False, verbose_name=_('Restaurante interno'))
    tem_bar          = models.BooleanField(default=False, verbose_name=_('Bar'))
    aceita_animais   = models.BooleanField(default=False, verbose_name=_('Aceita animais'))
    tem_ar_condicionado = models.BooleanField(default=False)
    servico_quarto   = models.BooleanField(default=False, verbose_name=_('Serviço de quarto'))

    politica_cancelamento = models.TextField(blank=True, verbose_name=_('Política de cancelamento'))
    regras_casa            = models.TextField(blank=True, verbose_name=_('Regras da casa'))
    
    foto          = models.ImageField(upload_to='alojamentos/hotel/%Y/', null=True, blank=True)

    class Meta:
        db_table            = 'empresas_hotel'
        verbose_name        = _('Hotel')
        verbose_name_plural = _('Hotéis')

    def __str__(self):
        return f'Hotel: {self.empresa.nome}'


class TipoQuarto(ModeloBase):
    """
    Tipos de quartos disponíveis num hotel.
    """

    class Tipo(models.TextChoices):
        SOLTEIRO = 'solteiro', _('Solteiro')
        DUPLO    = 'duplo',    _('Duplo')
        SUITE    = 'suite',    _('Suíte')
        FAMILIAR = 'familiar', _('Familiar')
        VIP      = 'vip',      _('VIP')

    hotel         = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='tipos_quarto')
    tipo          = models.CharField(max_length=20, choices=Tipo.choices)
    nome          = models.CharField(max_length=100, verbose_name=_('Nome do tipo'))
    descricao     = models.TextField(blank=True)
    capacidade    = models.PositiveSmallIntegerField(default=2, verbose_name=_('Capacidade (pessoas)'))
    preco_noite   = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Preço por noite (AOA)'))
    total_quartos = models.PositiveSmallIntegerField(default=1, verbose_name=_('Quantidade'))
    foto          = models.ImageField(upload_to='quartos/%Y/', null=True, blank=True)
    comodidades   = models.JSONField(default=list, blank=True, verbose_name=_('Comodidades do quarto'))
    
    

    class Meta:
        db_table = 'empresas_tipo_quarto'
        verbose_name        = _('Tipo de Quarto')
        verbose_name_plural = _('Tipos de Quarto')

    def __str__(self):
        return f'{self.hotel.empresa.nome} — {self.nome}'


# ============================================================
# RESTAURANTE
# ============================================================

class Restaurante(ModeloBase):
    """
    Dados específicos de Restaurantes.
    """

    class TipoCozinha(models.TextChoices):
        ANGOLANA   = 'angolana',   _('Angolana')
        AFRICANA   = 'africana',   _('Africana')
        PORTUGUESA = 'portuguesa', _('Portuguesa')
        INTERNACIONAL = 'internacional', _('Internacional')
        FRUTOS_MAR = 'frutos_mar', _('Frutos do Mar')
        FAST_FOOD  = 'fast_food',  _('Fast Food')
        VEGETARIANA = 'vegetariana', _('Vegetariana')
        OUTRA      = 'outra',      _('Outra')

    empresa         = models.OneToOneField(
        EmpresaTuristica,
        on_delete=models.CASCADE,
        related_name='restaurante',
        limit_choices_to={'tipo_empresa': 'restaurante'},
    )
    nome            = models.CharField(max_length=100, blank=True, null=True)
    tipo_cozinha    = models.CharField(max_length=30, choices=TipoCozinha.choices, default=TipoCozinha.ANGOLANA)
    capacidade      = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=_('Capacidade (pessoas)'))
    preco_medio     = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_('Preço médio por pessoa (AOA)'))
    faixa_preco     = models.CharField(
        max_length=5,
        choices=[('$','Económico'),('$$','Moderado'),('$$$','Premium'),('$$$$','Luxo')],
        default='$$',
    )
    tem_entrega     = models.BooleanField(default=False, verbose_name=_('Faz entregas'))
    tem_takeaway    = models.BooleanField(default=False, verbose_name=_('Take-away'))
    reserva_obrigatoria = models.BooleanField(default=False)
    aceita_cartao   = models.BooleanField(default=False, verbose_name=_('Aceita cartão'))
    tem_wifi        = models.BooleanField(default=False)
    especialidades  = models.TextField(blank=True, verbose_name=_('Especialidades'))
    endereco        = models.TextField(blank=True, null=True)
    
    foto            = models.ImageField(upload_to='alojamentos/restaurante/%Y/', null=True, blank=True)

    class Meta:
        db_table            = 'empresas_restaurante'
        verbose_name        = _('Restaurante')
        verbose_name_plural = _('Restaurantes')

    def __str__(self):
        return f'Restaurante: {self.empresa.nome}'


class ItemMenu(ModeloPublicavel):
    """
    Itens do menu de um restaurante.
    """

    class Categoria(models.TextChoices):
        ENTRADA    = 'entrada',    _('Entrada')
        PRATO_PRINCIPAL = 'prato_principal', _('Prato Principal')
        SOBREMESA  = 'sobremesa',  _('Sobremesa')
        BEBIDA     = 'bebida',     _('Bebida')
        PETISCO    = 'petisco',    _('Petisco')

    restaurante   = models.ForeignKey(Restaurante, on_delete=models.CASCADE, related_name='menu')
    categoria     = models.CharField(max_length=30, choices=Categoria.choices)
    nome          = models.CharField(max_length=200)
    descricao     = models.TextField(blank=True)
    ingredientes  = models.TextField(blank=True)
    preco         = models.DecimalField(max_digits=10, decimal_places=2)
    foto          = models.ImageField(upload_to='menus/%Y/', null=True, blank=True)
    vegetariano   = models.BooleanField(default=False)
    vegano        = models.BooleanField(default=False)
    sem_gluten    = models.BooleanField(default=False)
    picante       = models.BooleanField(default=False)
    mais_pedido   = models.BooleanField(default=False, verbose_name=_('Mais pedido'))

    class Meta:
        db_table            = 'empresas_item_menu'
        verbose_name        = _('Item do Menu')
        verbose_name_plural = _('Itens do Menu')
        ordering            = ['categoria', 'nome']

    def __str__(self):
        return f'{self.nome} — {self.restaurante.empresa.nome}'


# ============================================================
# GUIA TURÍSTICO
# ============================================================

class GuiaTuristico(ModeloBase):
    """
    Perfil de Guias Turísticos certificados.
    """

    class NivelExperiencia(models.TextChoices):
        JUNIOR   = 'junior',   _('Júnior (1-2 anos)')
        PLENO    = 'pleno',    _('Pleno (3-5 anos)')
        SENIOR   = 'senior',   _('Sénior (5+ anos)')
        EXPERT   = 'expert',   _('Expert / Especialista')

    usuario         = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='perfil_guia',
    )
    empresa         = models.OneToOneField(
        EmpresaTuristica,
        on_delete=models.CASCADE,
        related_name='guia',
        limit_choices_to={'tipo_empresa': 'guia'},
    )
    nivel_experiencia = models.CharField(max_length=20, choices=NivelExperiencia.choices, default=NivelExperiencia.JUNIOR)
    anos_experiencia  = models.PositiveSmallIntegerField(default=0)
    numero_licenca    = models.CharField(max_length=50, blank=True, unique=True, null=True, verbose_name=_('Nº de licença'))
    certificado       = models.FileField(upload_to='guias/certificados/', null=True, blank=True)
    foto       = models.FileField(upload_to='guias/fotos/', null=True, blank=True)

    # Idiomas falados
    idiomas = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Idiomas falados'),
        help_text=_('Ex.: ["pt","en","fr"]'),
    )

    # Províncias onde opera
    provincias_atuacao = models.ManyToManyField(
        Provincia,
        blank=True,
        related_name='guias',
        verbose_name=_('Províncias de atuação'),
    )

    # Especialidades
    especializacoes = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Especializações'),
        help_text=_('Ex.: ["natureza","cultura","aventura"]'),
    )

    # Tarifas
    preco_hora          = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_('Preço/hora (AOA)'))
    preco_dia_completo  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_('Preço/dia completo (AOA)'))
    disponivel          = models.BooleanField(default=True, verbose_name=_('Disponível'))

    # Métricas
    total_excursoes     = models.PositiveIntegerField(default=0)
    media_avaliacao     = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_avaliacoes    = models.PositiveIntegerField(default=0)

    class Meta:
        db_table            = 'empresas_guia_turistico'
        verbose_name        = _('Guia Turístico')
        verbose_name_plural = _('Guias Turísticos')

    def __str__(self):
        return f'Guia: {self.usuario.nome_completo}'