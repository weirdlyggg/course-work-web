from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from rest_framework.generics import ListAPIView
from .models import User, Product, Category, Review, Order
from .serializers import UserSerializer, ProductSerializer, CategorySerializer, ReviewSerializer, OrderSerializer
from rest_framework import generics

# Список пользователей
@api_view(['GET'])
def members(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

# Товары по категории
@api_view(['GET'])
def products_by_category(request, category_id):
    products = Product.objects.filter(category_id=category_id)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

# Исключение дорогих товаров
@api_view(['GET'])
def affordable_products(request):
    products = Product.objects.exclude(price__gt=10000)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

# Сортировка товаров
@api_view(['GET'])
def sorted_products(request):
    products = Product.objects.order_by('name')
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

# Детали товара
@api_view(['GET'])
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    serializer = ProductSerializer(product)
    return Response(serializer.data)

# Пагинация товаров
from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 5  

class ProductListView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = StandardResultsSetPagination

# Средняя цена товаров
@api_view(['GET'])
def average_price(request):
    average_price = Product.objects.aggregate(Avg('price'))
    return Response({'average_price': average_price['price__avg']})

# Регистрация пользователя
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import RegisterSerializer

from django.contrib.auth import login as auth_login

@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # Опционально: авто-вход после регистрации
        request.session['user_id'] = user.id
        return Response({'message': 'Пользователь зарегистрирован'})
    return Response(serializer.errors, status=400)

def members(request):
  myusers = User.objects.all().values() 
  template = loader.get_template('first.html')
  context = {
    'myusers' : myusers,
  }
  return HttpResponse(template.render(context, request))

from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

@api_view(['POST'])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})
    return Response({'error': 'Invalid credentials'}, status=400)

class ProductCreateAPIView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductUpdateAPIView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductDeleteAPIView(generics.DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# Пример select_related
class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.select_related('category').prefetch_related('images', 'favorites')
    serializer_class = ProductSerializer

@api_view(['GET'])
def latest_products(request):
    products = Product.objects.order_by('-id')[:5]  # или по created_at, если добавишь поле
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def latest_products(request):
    products = Product.objects.prefetch_related('images').order_by('-id')[:5]
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def current_user(request):
    user_id = request.session.get('user_id')  # Или используйте другой способ хранения
    if not user_id:
        return Response({'error': 'Не авторизован'}, status=401)
    
    try:
        user = User.objects.get(id=user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response({'error': 'Пользователь не найден'}, status=404)