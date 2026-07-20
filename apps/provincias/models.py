"""
============================================================
EXPLORA REGIÃO AI — apps/provincias/models.py
Províncias, Municípios e Património Geográfico
============================================================
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

from apps.authenticate.models import ModeloBase, ModeloPublicavel, Usuario, Midia


# ============================================================
# REGIÃO
# ============================================================

class Regiao(ModeloPublicavel):
    """
    Região que agrupa as províncias (ex.: Angola, Região Norte...).
    """
    nome        = models.CharField(max_length=150, unique=True, verbose_name=_('Nome'))
    slug        = models.SlugField(max_length=160, unique=True)
    descricao   = models.TextField(blank=True, verbose_name=_('Descrição'))
    logo        = models.ImageField(upload_to='regioes/logos/', null=True, blank=True)
    banner      = models.ImageField(upload_to='regioes/banners/', null=True, blank=True)
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
    meta_titulo       = models.CharField(max_length=70, blank=True)
    meta_descricao    = models.CharField(max_length=160, blank=True)

    class Meta:
        db_table            = 'provincias_regiao'
        verbose_name        = _('Região')
        verbose_name_plural = _('Regiões')

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)


# ============================================================
# PROVÍNCIA
# ============================================================

class Provincia(ModeloPublicavel):
    """
    Perfil completo de cada Província.
    """
    regiao      = models.ForeignKey(
        Regiao,
        on_delete=models.PROTECT,
        related_name='provincias',
        verbose_name=_('Região'),
    )
    nome        = models.CharField(max_length=150, verbose_name=_('Nome'))
    slug        = models.SlugField(max_length=160, unique=True)
    capital     = models.CharField(max_length=100, blank=True, verbose_name=_('Capital'))
    codigo_iso  = models.CharField(max_length=10, blank=True, unique=True, verbose_name=_('Código ISO'))
    ordem       = models.IntegerField(unique=True)
    # Conteúdo
    historia    = models.TextField(blank=True, verbose_name=_('História'))
    cultura     = models.TextField(blank=True, verbose_name=_('Cultura'))
    patrimonio  = models.TextField(blank=True, verbose_name=_('Património'))
    gastronomia = models.TextField(blank=True, verbose_name=_('Gastronomia'))
    festividades = models.TextField(blank=True, verbose_name=_('Festividades'))
    introducao  = models.TextField(blank=True, verbose_name=_('Introdução (resumo)'))

    # Mídia
    foto_capa   = models.ImageField(upload_to='provincias/capas/%Y/', null=True, blank=True)
    foto_banner = models.ImageField(upload_to='provincias/banners/%Y/', null=True, blank=True)
    midias      = models.ManyToManyField(Midia, blank=True, related_name='provincias')

    # Dados geográficos
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
    area_km2    = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name=_('Área (km²)'))

    # Dados estatísticos
    populacao   = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('População'))
    densidade_pop = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_('Densidade populacional (hab/km²)'))
    num_municipios = models.PositiveSmallIntegerField(default=0, verbose_name=_('Número de municípios'))

    # SEO
    meta_titulo    = models.CharField(max_length=70, blank=True)
    meta_descricao = models.CharField(max_length=160, blank=True)

    # Métricas de acesso
    total_visualizacoes = models.PositiveIntegerField(default=0)
    total_pesquisas     = models.PositiveIntegerField(default=0)

    class Meta:
        db_table            = 'provincias_provincia'
        verbose_name        = _('Província')
        verbose_name_plural = _('Províncias')
        ordering            = ['nome']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['regiao', 'status']),
        ]

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)


# ============================================================
# MUNICÍPIO
# ============================================================

class Municipio(ModeloPublicavel):
    """
    Municípios dentro de cada Província.
    """
    provincia   = models.ForeignKey(
        Provincia,
        on_delete=models.PROTECT,
        related_name='municipios',
        verbose_name=_('Província'),
    )
    nome        = models.CharField(max_length=150, verbose_name=_('Nome'))
    slug        = models.SlugField(max_length=160)
    descricao   = models.TextField(blank=True)
    diagnostico    = models.TextField(blank=True, verbose_name=_('Diagnóstico do Setor'))
    estrategia    = models.TextField(blank=True, verbose_name=_('Estrategia para potenciar o turismo'))
    caracteristicas    = models.TextField(blank=True, verbose_name=_('Caract. Demográfica, Física-Económico e Geografica'))
    geografica_limite    = models.TextField(blank=True, verbose_name=_('Situação Geográfica'))
    Relevo    = models.TextField(blank=True, verbose_name=_('Relevo e Geomorfologia'))
    clima_hidrografica    = models.TextField(blank=True, verbose_name=_('Clima e Hidrografia'))
    economia    = models.TextField(blank=True, verbose_name=_('Sócio Demográfico e Económico'))
    agricultura    = models.TextField(blank=True, verbose_name=_('Agricultura, indústria e pesca'))
    historia    = models.TextField(blank=True, verbose_name=_('História / Contexto'))
    
    foto_capa   = models.ImageField(upload_to='municipios/capas/%Y/', null=True, blank=True)
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
    area_km2    = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    populacao   = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        db_table            = 'provincias_municipio'
        verbose_name        = _('Município')
        verbose_name_plural = _('Municípios')
        unique_together     = [('provincia', 'slug')]
        ordering            = ['provincia', 'nome']

    def __str__(self):
        return f'{self.nome} — {self.provincia.nome}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)


# ============================================================
# CATEGORIAS DE PONTOS TURÍSTICOS
# ============================================================

class CategoriaTurismo(ModeloBase):
    """
    Categorias para classificar pontos turísticos, empresas, etc.
    Ex.: Praia, Montanha, Museu, Parque Natural, etc.
    """

    class Icone(models.TextChoices):
        PRAIA          = 'praia',          _('Praia')
        MONTANHA       = 'montanha',       _('Montanha')
        MUSEU          = 'museu',          _('Museu')
        PARQUE         = 'parque',         _('Parque Natural')
        PATRIMONIO     = 'patrimonio',     _('Património Histórico')
        GASTRONOMIA    = 'gastronomia',    _('Gastronomia')
        CULTURA        = 'cultura',        _('Cultura')
        AVENTURA       = 'aventura',       _('Aventura')
        RELIGIAO       = 'religiao',       _('Religioso')
        MERCADO        = 'mercado',        _('Mercado')
        OUTRO          = 'outro',          _('Outro')

    nome      = models.CharField(max_length=100, unique=True)
    slug      = models.SlugField(max_length=110, unique=True)
    icone     = models.CharField(max_length=30, choices=Icone.choices, default=Icone.OUTRO)
    descricao = models.TextField(blank=True)
    cor_hex   = models.CharField(max_length=7, default='#2196F3', verbose_name=_('Cor (hex)'))
    imagem    = models.ImageField(upload_to='categorias/', null=True, blank=True)

    class Meta:
        db_table            = 'provincias_categoria_turismo'
        verbose_name        = _('Categoria de Turismo')
        verbose_name_plural = _('Categorias de Turismo')
        ordering            = ['nome']

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)


# ============================================================
# PONTO TURÍSTICO
# ============================================================

class PontoTuristico(ModeloPublicavel):
    """
    Atracção turística de uma Província/Município.
    Inclui coordenadas PostGIS, avaliações e media.
    """
    provincia   = models.ForeignKey(
        Provincia,
        on_delete=models.PROTECT,
        related_name='pontos_turisticos',
        verbose_name=_('Província'),
    )
    municipio   = models.ForeignKey(
        Municipio,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='pontos_turisticos',
        verbose_name=_('Município'),
    )
    categorias  = models.ManyToManyField(
        CategoriaTurismo,
        blank=True,
        related_name='pontos_turisticos',
    )
    nome        = models.CharField(max_length=200, verbose_name=_('Nome'))
    slug        = models.SlugField(max_length=220, unique=True)
    descricao   = models.TextField(verbose_name=_('Descrição'))
    
    historia    = models.TextField(blank=True, verbose_name=_('História / Contexto'))
    proposta    = models.TextField(blank=True, verbose_name=_('Proposta de intervenção'))
    localizacao = models.TextField(blank=True, verbose_name=_('Localização'))
    outros_aspectos = models.TextField(blank=True, verbose_name=_('Outros Aspectos'))
    infrastrutura = models.TextField(blank=True, verbose_name=_('Infra-Estruturas'))
    via_acesso = models.TextField(blank=True, verbose_name=_('Via de Acesso'))
    especie_animal = models.TextField(blank=True, help_text='Só para Parques', verbose_name=_('Espécie Animal'))

    # Localização
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
    endereco    = models.CharField(max_length=300, blank=True, verbose_name=_('Endereço'))

    # Mídia
    foto_principal = models.ImageField(upload_to='pontos/%Y/%m/', null=True, blank=True)
    midias         = models.ManyToManyField(Midia, blank=True, related_name='pontos_turisticos')

    # Horários e acesso
    horario_funcionamento = models.JSONField(
        default=dict, blank=True,
        verbose_name=_('Horários por dia da semana'),
        help_text=_('Ex.: {"seg":"08:00-17:00","dom":"fechado"}'),
    )
    preco_entrada   = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_('Preço de entrada (AOA)'))
    entrada_gratuita = models.BooleanField(default=True, verbose_name=_('Entrada gratuita'))
    acessivel       = models.BooleanField(default=False, verbose_name=_('Acessível para mobilidade reduzida'))

    # Contacto
    telefone  = models.CharField(max_length=20, blank=True)
    email     = models.EmailField(blank=True)
    website   = models.URLField(blank=True)
    responsavel   = models.TextField(blank=True)

    melhor_epoca = models.TextField(blank=True, null=True)
    
    # Métricas
    media_avaliacao     = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_avaliacoes    = models.PositiveIntegerField(default=0)
    total_visualizacoes = models.PositiveIntegerField(default=0)

    # SEO
    meta_titulo    = models.CharField(max_length=70, blank=True)
    meta_descricao = models.CharField(max_length=160, blank=True)

    class Meta:
        db_table            = 'provincias_ponto_turistico'
        verbose_name        = _('Ponto Turístico')
        verbose_name_plural = _('Pontos Turísticos')
        ordering            = ['-destaque', 'nome']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['provincia', 'status']),
            models.Index(fields=['media_avaliacao']),
        ]

    def __str__(self):
        return f'{self.nome} ({self.provincia.nome})'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)


# ============================================================
# GASTRONOMIA TÍPICA
# ============================================================

class PratoTipico(ModeloPublicavel):
    """
    Pratos típicos e iguarias de cada Província.
    """
    provincia   = models.ForeignKey(
        Provincia,
        on_delete=models.CASCADE,
        related_name='pratos_tipicos',
    )
    nome        = models.CharField(max_length=200)
    slug        = models.SlugField(max_length=220, unique=True)
    descricao   = models.TextField()
    ingredientes = models.TextField(blank=True)
    modo_preparo = models.TextField(blank=True)
    foto        = models.ImageField(upload_to='gastronomia/%Y/', null=True, blank=True)
    vegetariano = models.BooleanField(default=False)
    destaque = models.BooleanField(default=False)
    faixa_preco = models.CharField(
        max_length=10,
        choices=[('$','Económico'),('$$','Moderado'),('$$$','Premium')],
        default='$',
    )

    class Meta:
        db_table            = 'provincias_prato_tipico'
        verbose_name        = _('Prato Típico')
        verbose_name_plural = _('Pratos Típicos')
        ordering            = ['provincia', 'nome']

    def __str__(self):
        return f'{self.nome} ({self.provincia.nome})'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)


# ============================================================
# FAVORITOS DO UTILIZADOR
# ============================================================

class Favorito(ModeloBase):
    """
    Pontos turísticos guardados como favoritos por um utilizador.
    """
    usuario        = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='favoritos',
    )
    ponto_turistico = models.ForeignKey(
        PontoTuristico,
        on_delete=models.CASCADE,
        related_name='salvos_por',
    )
    nota_pessoal   = models.TextField(blank=True, verbose_name=_('Nota pessoal'))

    class Meta:
        db_table        = 'provincias_favorito'
        verbose_name    = _('Favorito')
        unique_together = [('usuario', 'ponto_turistico')]

    def __str__(self):
        return f'{self.usuario} ❤ {self.ponto_turistico}'
    

class ConversaAI(ModeloBase):

    usuario=models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE
    )


    pergunta=models.TextField()


    resposta=models.TextField()


    contexto=models.JSONField()
