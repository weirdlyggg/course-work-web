from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Avg
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
# pylint: disable=no-member
from .models import Product, SaleEvent, Order
from .serializers import ProductSerializer, OrderSerializer

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100

class ProductViewSet(viewsets.ModelViewSet):
    """
    CRUD для товаров + доп. методы: top_rated, recommend, on_sale
    + DRF-фильтрация по category и по диапазону цены.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = StandardResultsSetPagination

    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'category': ['exact'],
        'price': ['gte', 'lte'],
    }

    @action(detail=False, methods=['get'], url_path='top-rated')
    def top_rated_products(self, request):
        qs = Product.objects.annotate(avg_rating=Avg('review__rating')) \
                             .order_by('-avg_rating')[:10]
        return Response(self.get_serializer(qs, many=True).data)

    @action(detail=True, methods=['get'], url_path='recommend')
    def recommend_products(self, request, pk=None):
        prod = self.get_object()
        qs = Product.objects.filter(category=prod.category) \
                            .exclude(pk=prod.pk)[:5]
        return Response(self.get_serializer(qs, many=True).data)

    @action(detail=False, methods=['get'], url_path='on_sale')
    def on_sale(self, request):
        now = timezone.now()
        sale = SaleEvent.objects.filter(end_time__gt=now).first()
        if not sale:
            return Response([], status=status.HTTP_200_OK)
        qs = Product.objects.filter(category=sale.category)
        return Response(self.get_serializer(qs, many=True).data)

class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Только чтение заказов, но — **только** текущего аутентифицированного пользователя.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # будем отдавать только свои заказы
        return Order.objects.filter(user=self.request.user)
