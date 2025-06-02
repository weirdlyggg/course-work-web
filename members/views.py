from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render
from django.db.models import Avg
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView, RetrieveAPIView
from .models import User, Product, Category, Review, Order
from .serializers import UserSerializer, ProductSerializer, CategorySerializer, ReviewSerializer, OrderSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
import random


def home(request):
    featured_products = Product.objects.filter(is_featured=True)[:6]
    recommended_products = Product.objects.order_by('?')[:12]

    return render(request, 'home.html', {
        'featured_products': featured_products,
        'recommended_products': recommended_products
    })

# --- API: Пользователи ---
@api_view(['GET'])
def api_members(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

# --- API: Продукты по категориям, фильтрации и сортировке ---
@api_view(['GET'])
def products_by_category(request, category_id):
    products = Product.objects.filter(category_id=category_id)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def affordable_products(request):
    products = Product.objects.exclude(price__gt=10000)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def sorted_products(request):
    products = Product.objects.order_by('name')
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

# --- API: Детали товара ---
@api_view(['GET'])
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    serializer = ProductSerializer(product)
    return Response(serializer.data)

# --- API: Пагинация товаров ---
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 5

class ProductListView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = StandardResultsSetPagination

# --- API: Средняя цена всех товаров ---
@api_view(['GET'])
def average_price(request):
    average = Product.objects.aggregate(Avg('price'))
    return Response({'average_price': average['price__avg']})

# --- API: Регистрация пользователя ---
from .serializers import RegisterSerializer

@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Пользователь зарегистрирован'})
    return Response(serializer.errors, status=400)

# --- API: Логин пользователя ---
@api_view(['POST'])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})
    return Response({'error': 'Неверные учетные данные'}, status=400)

# --- API: CRUD товары ---
class ProductCreateAPIView(CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductUpdateAPIView(UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductDeleteAPIView(DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# --- API: Подробно с prefetch/select_related ---
class ProductDetailView(RetrieveAPIView):
    queryset = Product.objects.select_related('category').prefetch_related('images', 'favorites')
    serializer_class = ProductSerializer

# --- API: Новинки ---
@api_view(['GET'])
def latest_products(request):
    products = Product.objects.prefetch_related('images').order_by('-id')[:5]
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

# --- API: Текущий пользователь ---
@api_view(['GET'])
def current_user(request):
    if request.user.is_authenticated:
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    return Response({'error': 'Не авторизован'}, status=401)

# --- HTML: Страница участников (для шаблона) ---
def members_page(request):
    myusers = User.objects.all()
    return render(request, 'first.html', {'myusers': myusers})

# --- HTML: Главная страница с новинками ---
def home(request):
    latest_products = Product.objects.prefetch_related('images').order_by('-id')[:5]
    return render(request, 'home.html', {'latest_products': latest_products})
