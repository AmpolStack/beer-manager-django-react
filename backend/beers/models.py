from django.db import models


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    country = models.CharField(max_length=100, blank=True, verbose_name="País")
    founded_year = models.PositiveIntegerField(null=True, blank=True, verbose_name="Año de fundación")
    description = models.TextField(blank=True, verbose_name="Descripción")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado en")

    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
        ordering = ['name']

    def __str__(self):
        return self.name


class Beer(models.Model):
    BEER_TYPES = [
        ('lager', 'Lager'),
        ('ale', 'Ale'),
        ('stout', 'Stout'),
        ('porter', 'Porter'),
        ('ipa', 'IPA'),
        ('wheat', 'Wheat Beer'),
        ('sour', 'Sour'),
        ('other', 'Otro'),
    ]

    name = models.CharField(max_length=100, verbose_name="Nombre")
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='beers',
        verbose_name="Marca"
    )
    beer_type = models.CharField(max_length=20, choices=BEER_TYPES, default='lager', verbose_name="Tipo")
    alcohol_content = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name="Contenido de alcohol (%)"
    )
    ibu = models.PositiveIntegerField(null=True, blank=True, verbose_name="IBU")
    description = models.TextField(blank=True, verbose_name="Descripción")
    image_url = models.URLField(blank=True, verbose_name="URL de imagen")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado en")

    class Meta:
        verbose_name = "Cerveza"
        verbose_name_plural = "Cervezas"
        ordering = ['brand__name', 'name']

    def __str__(self):
        return f"{self.name} ({self.brand.name})"