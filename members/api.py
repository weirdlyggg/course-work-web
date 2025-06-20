from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Product, SaleEvent
from .serializers import ProductSerializer
from django.db.models import Avg


class ProductViewSet(viewsets.ModelViewSet):
    """
    Стандартный CRUD + дополнительные эндпоинты:
      - GET  /api/products/top-rated/
      - GET  /api/products/{pk}/recommend/
      - GET  /api/products/on_sale/
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(detail=False, methods=['get'], url_path='top-rated')
    def top_rated_products(self, request):
        # Топ-10 по средней оценке (нужен Review.aggregate)
        qs = (
            Product.objects
                   .annotate(avg_rating=Avg('review__rating'))
                   .order_by('-avg_rating')[:10]
        )
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='recommend')
    def recommend_products(self, request, pk=None):
        # 5 похожих из той же категории
        prod = self.get_object()
        qs = Product.objects.filter(category=prod.category).exclude(pk=prod.pk)[:5]
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='on_sale')
    def on_sale(self, request):
        """
        Список товаров текущей распродажи
        """
        now = timezone.now()
        sale = SaleEvent.objects.filter(end_time__gt=now).first()
        if not sale:
            return Response([], status=status.HTTP_200_OK)

        qs = Product.objects.filter(category=sale.category)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
