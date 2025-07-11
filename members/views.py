from django.views.generic import View, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import F, Avg, Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    UpdateAPIView,
    DestroyAPIView,
    RetrieveAPIView
)
from rest_framework.authtoken.models import Token
# pylint: disable=no-member
from .models import (
    Product,
    Category,
    Review,
    Order,
    Gemestone,
    SaleEvent,
    OrderItem
)
from .serializers import (
    UserSerializer,
    ProductSerializer
)
from .forms import (
    OrderReviewForm,
    UserProfileForm,
    CustomUserRegistrationForm,
    ProductForm,
)

@api_view(['GET'])
def top_rated_products(request):
    """
    GET /api/products/top-rated/
    Возвращает 10 товаров с наивысшим средним рейтингом.
    """
    # Аннотируем каждый товар его avg_rating и сортируем
    qs = (
        Product.objects
               .annotate(avg_rating=Avg('review__rating'))
               .filter(avg_rating__isnull=False)
               .order_by('-avg_rating')[:10]
    )
    serializer = ProductSerializer(qs, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
def recommend_products(request, pk):
    """
    GET /api/products/{pk}/recommend/
    Возвращает до 5 товаров из той же категории (без самого себя).
    """
    product = get_object_or_404(Product, pk=pk)
    qs = (
        Product.objects
               .filter(category=product.category)
               .exclude(pk=product.pk)[:5]
    )
    serializer = ProductSerializer(qs, many=True, context={'request': request})
    return Response(serializer.data)

# === HTML Views ===
class ProductDetailView(View):
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        # Increase view count
        Product.objects.filter(pk=pk).update(view_count=F('view_count') + 1)
        product.refresh_from_db(fields=['view_count'])
        # Active sale event for this category
        sale_event = SaleEvent.objects.filter(
            category=product.category,
            end_time__gt=timezone.now()
        ).first()
        # Load reviews
        reviews = (
            Review.objects
            .filter(product=product)
            .select_related('user')
            .order_by('-created_at')
        )
        # Popular products
        popular_products = Product.objects.order_by('-view_count')[:6]
        # Подборка «похожих»: до 5 товаров из той же категории
        similar_products = (
            Product.objects
                .filter(category=product.category)
                .exclude(pk=product.pk)[:5]
        )
        return render(request, 'product_detail.html', {
            'product': product,
            'sale_event': sale_event,
            'reviews': reviews,
            'popular_products': popular_products,
            'similar_products': similar_products,
        })


def catalog(request):
    q = request.GET.get('q', '').strip()
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    discount_only = request.GET.get('discount_only') == 'on'
    hide_empty = request.GET.get('hide_empty') == 'on'
    category_id = request.GET.get('category')
    gemestone_id = request.GET.get('gemestone')
    # базовый queryset
    products_qs = Product.objects.all()
    # 1) Поиск: имя **ИЛИ** описание **И** status='available'
    if q:
        products_qs = products_qs.filter(
            (Q(name__icontains=q) | Q(description__icontains=q)) &
            Q(status='available')
        )
    # 2) Фильтр «только с картинками» и «не скрытые»
    if hide_empty:
        products_qs = products_qs.filter(
            ~Q(images__isnull=True),    # has at least one image
            ~Q(status='hidden')         # статус не hidden
        ).distinct()
    # 3) Диапазон цены
    if min_price:
        products_qs = products_qs.filter(price__gte=min_price)
    if max_price:
        products_qs = products_qs.filter(price__lte=max_price)
    # 4) Только со скидкой (если галочка)
    if discount_only:
        now = timezone.now()
        products_qs = products_qs.filter(
            category__saleevent__end_time__gt=now
        ).distinct()
    # 5) Категории и камни
    if category_id:
        products_qs = products_qs.filter(category_id=category_id)
    if gemestone_id:
        products_qs = products_qs.filter(gemestones__id=gemestone_id)
    # пагинация
    paginator   = Paginator(products_qs, 12)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    # считаем цену со скидкой для отображения
    now        = timezone.now()
    sale_event = SaleEvent.objects.filter(end_time__gt=now).first()
    for prod in page_obj:
        if sale_event and prod.category_id == sale_event.category_id:
            prod.sale_price = prod.price * (100 - sale_event.discount) / 100
        else:
            prod.sale_price = None

    return render(request, 'catalog.html', {
        'products':          page_obj,
        'page_obj':          page_obj,
        'paginator':         paginator,
        'all_names':         Product.objects.values_list('name', flat=True).distinct(),
        'categories':        Category.objects.all(),
        'gemestones':        Gemestone.objects.all(),
        'search_query':      q,
        'min_price':         min_price or '',
        'max_price':         max_price or '',
        'discount_only':     discount_only,
        'hide_empty':        hide_empty,
        'selected_category': category_id or '',
        'selected_gemestone':gemestone_id or '',
    })


def home(request):
    latest_products = Product.objects.filter(status='available').order_by('-created_at')[:5]
    popular_products = Product.objects.filter(status='available').order_by('-view_count')[:6]
    sale_event = SaleEvent.objects.filter(end_time__gt=timezone.now()).first()
    sale_products = []
    if sale_event:
        for p in Product.objects.filter(category=sale_event.category, status='available'):
            discount_price = p.price * (100 - sale_event.discount) / 100
            sale_products.append({
                'product': p,
                'old_price': p.price,
                'new_price': f"{discount_price:.2f}",
            })
    top_rated_products = (
        Product.objects
            .annotate(avg_rating=Avg('review__rating'))
            .filter(avg_rating__isnull=False)
            .order_by('-avg_rating')[:6]
    )
    return render(request, 'home.html', {
        'latest_products': latest_products,
        'popular_products': popular_products,
        'sale_event': sale_event,
        'sale_products': sale_products,
        'top_rated_products': top_rated_products,
    })


def members_page(request):
    return render(request, 'first.html', {'myusers': Product.objects.none()})

# === API Views ===
@api_view(['GET'])
def api_members(request):
    return Response(UserSerializer(User.objects.all(), many=True).data)

@api_view(['GET'])
def products_by_category(request, category_id):
    return Response(ProductSerializer(
        Product.objects.filter(category_id=category_id), many=True
    ).data)

@api_view(['GET'])
def affordable_products(request):
    return Response(ProductSerializer(
        Product.objects.exclude(price__gt=10000), many=True
    ).data)

@api_view(['GET'])
def sorted_products(request):
    return Response(ProductSerializer(
        Product.objects.order_by('name'), many=True
    ).data)

@api_view(['GET'])
def latest_products(request):
    qs = Product.objects.prefetch_related('images').order_by('-id')[:5]
    return Response(ProductSerializer(qs, many=True).data)

@api_view(['GET'])
def average_price(request):
    avg = Product.objects.aggregate(Avg('price'))['price__avg']
    return Response({'average_price': avg})

class ProductDetailAPIView(RetrieveAPIView):
    queryset = Product.objects.select_related('category').prefetch_related('images', 'favorites')
    serializer_class = ProductSerializer

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 5

class ProductListView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = StandardResultsSetPagination

@api_view(['POST'])
def login_user(request):
    user = authenticate(
        request,
        username=request.data.get('username'),
        password=request.data.get('password')
    )
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})
    return Response({'error': 'Invalid credentials'}, status=400)

@api_view(['GET'])
def current_user(request):
    if request.user.is_authenticated:
        return Response(UserSerializer(request.user).data)
    return Response({'error': 'Not authenticated'}, status=401)

class ProductCreateAPIView(CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductUpdateAPIView(UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductDeleteAPIView(DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

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
    orders_count = orders.count()
    has_orders = orders.exists()

    products = Product.objects.all() if user.is_staff else []

    return render(request, 'profile.html', {
    'user': user,
    'user_form': form,
    'orders': orders,
    'orders_count': orders_count,
    'has_orders': has_orders,
    'products': products,
})

@login_required
def add_to_cart(request, product_id):
    cart = request.session.get('cart', [])
    product = get_object_or_404(Product, id=product_id)
    if product_id not in cart:
        cart.append(product_id)
    request.session['cart'] = cart
    return redirect('product_detail', pk=product_id)

@login_required
def checkout_view(request):
    # 1) Получаем список ID товаров из сессии (по умолчанию пустой список)
    cart_ids = request.session.get('cart', [])
    if not cart_ids:
        # если корзина пуста — перенаправляем обратно
        return redirect('cart')

    user = request.user
    now = timezone.now()
    sale_event = SaleEvent.objects.filter(end_time__gt=now).first()

    # 2) Достаём продукты
    products = list(Product.objects.filter(id__in=cart_ids))

    # 3) Вешаем sale_price на каждый продукт
    for p in products:
        if sale_event and p.category_id == sale_event.category_id:
            p.sale_price = p.price * (100 - sale_event.discount) / 100
        else:
            p.sale_price = None

    # 4) Считаем общую сумму, отдавая приоритет sale_price
    total = sum(p.sale_price or p.price for p in products)

    # Валидация суммы заказа: от 100 до 100 000 ₽
    if total < 100 or total > 100000:
        messages.error(
            request,
            "Сумма заказа должна быть не менее 100 ₽ и не более 100 000 ₽. "
            f"Текущая сумма: {total:.2f} ₽."
        )
        return redirect('cart')

    # 5) Создаём сам Order
    order = Order.objects.create(
        user        = user,
        total_price = total,
        status      = 'pending'
    )

    # 6) И каждый OrderItem
    for p in products:
        price_to_use = p.sale_price or p.price
        OrderItem.objects.create(
            order                     = order,
            product                   = p,
            quantity                  = 1,
            prise_at_time_of_purchase = price_to_use
        )

    # 7) Очищаем корзину и редирект в профиль
    request.session['cart'] = []
    return redirect('profile')



def cart_view(request):
    cart_ids = request.session.get('cart', [])
    products = Product.objects.filter(id__in=cart_ids)
    now = timezone.now()
    sale_event = SaleEvent.objects.filter(end_time__gt=now).first()
    for p in products:
        if sale_event and p.category_id == sale_event.category_id:
            p.sale_price = p.price * (100 - sale_event.discount) / 100
        else:
            p.sale_price = None
    return render(request, 'cart.html', {
        'products': products,
    })

@login_required
def order_detail_view(request, pk):
    order = (
        get_object_or_404(Order, pk=pk)
        if request.user.is_staff else
        get_object_or_404(Order, pk=pk, user=request.user)
    )
    items = list(order.items.select_related('product').all())
    existing = Review.objects.filter(
        user=request.user,
        product__in=[i.product for i in items]
    )
    by_prod = {r.product_id: r for r in existing}
    form = OrderReviewForm(request.POST or None)
    if request.method == 'POST' and order.status == 'delivered' and form.is_valid():
        prod_id = int(request.POST.get('product_id'))
        match = next((i for i in items if i.product.id == prod_id), None)
        if match and not by_prod.get(prod_id):
            rev = form.save(commit=False)
            rev.user = request.user
            rev.product = match.product
            rev.save()
            return redirect('order_detail', pk=pk)
    # attach line totals and existing reviews
    for item in items:
        item.line_total = item.quantity * item.prise_at_time_of_purchase
        item.review = by_prod.get(item.product.id)
    return render(request, 'order_detail.html', {
        'order': order,
        'order_items': items,
        'form': form,
    })

# Admin CRUD views
class AdminProductEditView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    success_url = '/profile/'
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs) if request.user.is_staff else redirect('home')

class AdminProductDeleteView(DeleteView):
    model = Product
    template_name = 'product_confirm_delete.html'
    success_url = '/profile/'
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs) if request.user.is_staff else redirect('home')

@user_passes_test(lambda u: u.is_staff)
def create_product_view(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('profile')
    return render(request, 'product_form.html', {'form': form})

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

def register_view(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('profile')
    else:
        form = CustomUserRegistrationForm()
    return render(request, 'register.html', {'form': form})

# Пример 1: ищем все «кольца» или «серьги» стоимостью от 5000 ₽, но НЕ скрытые (status!='hidden')
@api_view(['GET'])
def rings_or_earrings_expensive(request):
    qs = Product.objects.filter(
        (Q(name__icontains='кольцо') | Q(name__icontains='серьга'))
        & Q(price__gte=5000)
        & ~Q(status='hidden')
    )
    data = ProductSerializer(qs, many=True, context={'request': request}).data
    return Response(data)

# Пример 2: выбираем товары с «золотом» в описании или «серебром» в названии,
# у которых более 100 просмотров, но НЕ те, у которых статус='out_of_stock'
@api_view(['GET'])
def gold_or_silver_popular(request):
    qs = Product.objects.filter(
        (Q(description__icontains='золото') | Q(name__icontains='серебро'))
        & Q(view_count__gt=100)
        & ~Q(status='out_of_stock')
    )
    data = ProductSerializer(qs, many=True, context={'request': request}).data
    return Response(data)
