from django.db.models import Count
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Brand, Beer
from .serializers import BrandSerializer, BeerSerializer


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.annotate(beers_count=Count('beers'))
    serializer_class = BrandSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'country']
    ordering_fields = ['name', 'country', 'founded_year', 'created_at', 'beers_count']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def beers(self, request, pk=None):
        brand = self.get_object()
        beers = brand.beers.filter(is_active=True)
        serializer = BeerSerializer(beers, many=True)
        return Response(serializer.data)


class BeerViewSet(viewsets.ModelViewSet):
    queryset = Beer.objects.select_related('brand').all()
    serializer_class = BeerSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['brand', 'beer_type', 'is_active']
    search_fields = ['name', 'brand__name', 'description']
    ordering_fields = ['name', 'alcohol_content', 'ibu', 'created_at']
    ordering = ['brand__name', 'name']

    def get_queryset(self):
        queryset = super().get_queryset()
        brand_id = self.request.query_params.get('brand_id')
        if brand_id:
            queryset = queryset.filter(brand_id=brand_id)
        return queryset

    @action(detail=False, methods=['get'])
    def types(self, request):
        types = [{'value': choice[0], 'label': choice[1]} for choice in Beer.BEER_TYPES]
        return Response(types)