from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BrandViewSet, BeerViewSet

router = DefaultRouter()
router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'beers', BeerViewSet, basename='beer')

urlpatterns = [
    path('', include(router.urls)),
]