# views.py

# Импорты стандартных библиотек
from django.views.generic import View
from django.shortcuts import get_object_or_404, render
from django.db.models import Count, Avg
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q

# Импорты DRF
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    UpdateAPIView,
    DestroyAPIView,
    RetrieveAPIView,
)
from rest_framework.authtoken.models import Token

# Локальные импорты
from .models import Product, Category, Review, Order, Gemestone, ProductImg
from .serializers import UserSerializer, ProductSerializer, CategorySerializer, ReviewSerializer, OrderSerializer, RegisterSerializer


# === HTML Views ===

class ProductDetailView(View):
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        recommended_products = Product.objects.exclude(pk=pk).order_by('?')[:5]
        return render(request, 'product_detail.html', {
            'product': product,
            'recommended_products': recommended_products,
        })


def catalog(request):
    category_id = request.GET.get('category')
    gemestone_id = request.GET.get('gemestone')

    products = Product.objects.all()

    if category_id:
        products = products.filter(category_id=category_id)

    if gemestone_id:
        products = products.filter(gemestones__id=gemestone_id)

    categories = Category.objects.all()
    gemestones = Gemestone.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'gemestones': gemestones,
        'selected_category': int(category_id) if category_id else None,
        'selected_gemestone': int(gemestone_id) if gemestone_id else None,
    }

    return render(request, 'catalog.html', context)


def home(request):
    recommended_products = Product.objects.filter(images__isnull=False).order_by('?')[:5]
    popular_products = Product.objects.filter(images__isnull=False).order_by('?')[:6]

    return render(request, 'home.html', {
        'recommended_products': recommended_products,
        'popular_products': popular_products
    })


def members_page(request):
    myusers = User.objects.all()
    return render(request, 'first.html', {'myusers': myusers})


# === API Views ===

@api_view(['GET'])
def api_members(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


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


@api_view(['GET'])
def latest_products(request):
    products = Product.objects.prefetch_related('images').order_by('-id')[:5]
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def average_price(request):
    average = Product.objects.aggregate(Avg('price'))
    return Response({'average_price': average['price__avg']})


# --- API: Подробно с prefetch/select_related ---
class ProductDetailAPIView(RetrieveAPIView):
    queryset = Product.objects.select_related('category').prefetch_related('images', 'favorites')
    serializer_class = ProductSerializer


# --- API: Пагинация товаров ---
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 5


class ProductListView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = StandardResultsSetPagination


# --- API: Регистрация пользователя ---
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


# --- API: Текущий пользователь ---
@api_view(['GET'])
def current_user(request):
    if request.user.is_authenticated:
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    return Response({'error': 'Не авторизован'}, status=401)


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