from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from .views import AdminProductEditView, AdminProductDeleteView
import debug_toolbar
from django.urls import include
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Сначала HTML-страницы
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    # Маршрут для профиля (личного кабинета)
    path('profile/', views.profile_view, name='profile'),
    
    # Маршрут для входа через HTML-форму
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    
    # Маршрут для регистрации
    path('register/', views.register_view, name='register'),

    
    # Маршрут для выхода
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('members-page/', views.members_page, name='members_page'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('admin/products/<int:pk>/edit/', AdminProductEditView.as_view(), name='product_update'),
    path('admin/products/<int:pk>/delete/', AdminProductDeleteView.as_view(), name='product_delete'),
    path('admin/products/create/', views.create_product_view, name='product_create_form'),



    # Теперь API
    path('api/products/latest/', views.latest_products, name='latest_products'),
    path('api/products/create/', views.ProductCreateAPIView.as_view(), name='product_create'),
    path('api/products/<int:pk>/delete/', views.ProductDeleteAPIView.as_view(), name='product_delete'),
    path('api/products/<int:pk>/', views.ProductDetailAPIView.as_view(), name='product_detail_api'),
    path('api/products/category/<int:category_id>/', views.products_by_category, name='products_by_category'),
    path('api/products/affordable/', views.affordable_products, name='affordable_products'),
    path('api/products/sorted/', views.sorted_products, name='sorted_products'),
    path('api/products/list/', views.ProductListView.as_view(), name='product_list'),
    path('api/products/average-price/', views.average_price, name='average_price'),
    path('api/login/', views.login_user, name='login'),
    path('api/members/me/', views.current_user, name='current_user'),
]

# Добавляем медиа-файлы только в режиме DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]