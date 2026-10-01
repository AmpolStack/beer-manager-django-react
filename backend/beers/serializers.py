from rest_framework import serializers
from .models import Brand, Beer


class BrandSerializer(serializers.ModelSerializer):
    beers_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Brand
        fields = ['id', 'name', 'country', 'founded_year', 'description', 'beers_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class BeerSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    brand_detail = BrandSerializer(source='brand', read_only=True)

    class Meta:
        model = Beer
        fields = [
            'id', 'name', 'brand', 'brand_name', 'brand_detail',
            'beer_type', 'alcohol_content', 'ibu', 'description',
            'image_url', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_alcohol_content(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("El contenido de alcohol debe estar entre 0 y 100%")
        return value

    def validate_ibu(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("El IBU no puede ser negativo")
        return value