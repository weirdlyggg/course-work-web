# views.py

# Импорты стандартных библиотек
from django.views.generic import View
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Count, Avg
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import F
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage



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
from .models import Product, Category, Review, Order, Gemestone, ProductImg, SaleEvent, OrderItem
from .serializers import UserSerializer, ProductSerializer, CategorySerializer, ReviewSerializer, OrderSerializer, RegisterSerializer


# === HTML Views ===

class ProductDetailView(View):
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        # ——— увеличить счётчик просмотров ——
        # увеличиваем счётчик просмотров через F-выражение
        Product.objects.filter(pk=product.pk).update(view_count=F('view_count') + 1)
        # подгружаем обновлённое значение обратно в объект
        product.refresh_from_db(fields=['view_count'])
        recommended_products = Product.objects.exclude(pk=pk).order_by('?')[:5]
        return render(request, 'product_detail.html', {
            'product': product,
            'recommended_products': recommended_products,
        })


def catalog(request):
    category_id = request.GET.get('category')
    gemestone_id = request.GET.get('gemestone')
    q = request.GET.get('q')

    # 1) Собираем базовый queryset
    products_qs = Product.objects.all()

    # 2) Фильтруем
    if category_id:
        products_qs = products_qs.filter(category_id=category_id)
    if gemestone_id:
        products_qs = products_qs.filter(gemestones__id=gemestone_id)
    if q:
        products_qs = products_qs.filter(name__icontains=q)

    # 3) Пагинация: 12 товаров на страницу
    paginator = Paginator(products_qs, 12)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # 4) Остальные данные для шаблона
    all_names   = Product.objects.values_list('name', flat=True).distinct()
    categories  = Category.objects.all()
    gemestones  = Gemestone.objects.all()

    return render(request, 'catalog.html', {
        # В шаблоне мы теперь используем page_obj для пагинации
        'products':       page_obj,  
        'page_obj':       page_obj,
        'paginator':      paginator,

        'all_names':      all_names,
        'categories':     categories,
        'gemestones':     gemestones,
        'search_query':   q or '',
        'selected_category':  category_id or '',
        'selected_gemestone': gemestone_id or '',
    })


from django.utils import timezone

def home(request):
    # 1) Последние — 5 самых свежих
    latest_products = Product.objects.filter(status='available').order_by('-created_at')[:5]
    # 2) Популярные — 6 по количеству просмотров
    popular_products = Product.objects.filter(status='available').order_by('-view_count')[:6]
    # 3) Распродажа — товары из категории события, со скидкой
    now = timezone.now()
    sale_event = SaleEvent.objects.filter(end_time__gt=now).first()
    sale_products = []
    if sale_event:
        qs = Product.objects.filter(category=sale_event.category, status='available')
        for p in qs:
            discounted = p.price * (100 - sale_event.discount) / 100
            sale_products.append({
                'product': p,
                'old_price': p.price,
                'new_price': f"{discounted:.2f}"
            })

    return render(request, 'home.html', {
        'latest_products': latest_products,
        'popular_products': popular_products,
        'sale_event': sale_event,
        'sale_products': sale_products,
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

from .forms import UserProfileForm
from .models import User

@login_required
def profile_view(request):
    user = request.user
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user)
    
    orders = user.orders.all()
    orders_count = orders.count()    # сколько всего заказов
    has_orders = orders.exists()     # есть ли хотя бы один заказ?

    products = Product.objects.all() if user.is_staff else None

    return render(request, 'profile.html', {
        'user': user,
        'user_form': form,
        'orders': orders,
        'orders_count': orders_count,
        'has_orders': has_orders,
        'products': products,
    })


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Получаем или создаём корзину в сессии
    cart = request.session.get('cart', [])
    
    # Добавляем товар в корзину (можно сделать проверку на дубли)
    if product_id not in cart:
        cart.append(product_id)
    
    request.session['cart'] = cart  # Сохраняем обновлённую корзину
    return redirect('product_detail', pk=product_id)

def checkout_view(request):
    cart_product_ids = request.session.get('cart', [])
    if not cart_product_ids:
        return redirect('cart')  # Если корзина пуста, редиректим обратно

    user = request.user
    products = Product.objects.filter(id__in=cart_product_ids)

    # Создаём заказ
    order = Order.objects.create(
        user=user,
        total_price=sum(p.price for p in products),
        status='pending'
    )

    # Создаём элементы заказа
    for product in products:
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=1,
            prise_at_time_of_purchase=product.price
        )

    # Очищаем корзину после оформления
    request.session['cart'] = []

    return redirect('profile')

from .models import Product

def cart_view(request):
    # Получаем список ID товаров из сессии
    cart_product_ids = request.session.get('cart', [])
    
    # Получаем сами товары из базы данных
    products = Product.objects.filter(id__in=cart_product_ids)

    return render(request, 'cart.html', {
        'products': products
    })

from django.views.generic import UpdateView, DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin
from .forms import ProductForm

class AdminProductEditView(UserPassesTestMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    success_url = '/profile/'

    def test_func(self):
        return self.request.user.is_staff

class AdminProductDeleteView(UserPassesTestMixin, DeleteView):
    model = Product
    template_name = 'product_confirm_delete.html'
    success_url = '/profile/'

    def test_func(self):
        return self.request.user.is_staff

from django.contrib.auth.decorators import user_passes_test
from .forms import ProductForm

@user_passes_test(lambda u: u.is_staff)
def create_product_view(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('profile'))
    else:
        form = ProductForm()
    
    return render(request, 'product_form.html', {'form': form})

from .forms import CustomUserRegistrationForm
from django.contrib.auth import login

def register_view(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # хешируем
            user.save()
            login(request, user)  # логиним сразу
            return redirect('profile')
    else:
        form = CustomUserRegistrationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def order_detail_view(request, pk):
    if request.user.is_staff:
        order = get_object_or_404(Order, pk=pk)
    else:
        order = get_object_or_404(Order, pk=pk, user=request.user)

    order_items = order.items.select_related('product').all()

    # Вычисляем итоговую цену для каждой позиции
    for item in order_items:
        item.line_total = item.quantity * item.prise_at_time_of_purchase

    return render(request, 'order_detail.html', {
        'order': order,
        'order_items': order_items,
    })
