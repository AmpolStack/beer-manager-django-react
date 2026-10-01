from django.contrib import admin
from .models import Brand, Beer


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'founded_year', 'created_at']
    list_filter = ['country', 'created_at']
    search_fields = ['name', 'country']
    ordering = ['name']


@admin.register(Beer)
class BeerAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'beer_type', 'alcohol_content', 'ibu', 'is_active']
    list_filter = ['brand', 'beer_type', 'is_active', 'created_at']
    search_fields = ['name', 'brand__name', 'description']
    ordering = ['brand__name', 'name']
    list_editable = ['is_active']