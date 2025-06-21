from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter
import debug_toolbar

from . import views
from .views import AdminProductEditView, AdminProductDeleteView
from .api import ProductViewSet, OrderViewSet

# инициализируем роутер
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'orders',    OrderViewSet,   basename='order')

urlpatterns = [
     # Сначала HTML-страницы
     path('', views.home, name='home'),
     path('catalog/', views.catalog, name='catalog'),
     path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),

     path('profile/', views.profile_view, name='profile'),
     path('register/', views.register_view, name='register'),
     path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
     path('accounts/logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

     path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
     path('cart/', views.cart_view, name='cart'),
     path('checkout/', views.checkout_view, name='checkout'),

     path('admin/products/<int:pk>/edit/', AdminProductEditView.as_view(), name='product_update'),
     path('admin/products/<int:pk>/delete/', AdminProductDeleteView.as_view(),
          name='product_delete'),
     path('admin/products/create/', views.create_product_view, name='product_create_form'),

     path('members-page/', views.members_page, name='members_page'),

     path('orders/<int:pk>/', views.order_detail_view, name='order_detail'),

     path('api/', include(router.urls)),

     # Теперь API
     path('api/products/latest/', views.latest_products, name='latest_products'),
     path('api/products/create/', views.ProductCreateAPIView.as_view(),
          name='product_create'),
     path('api/products/<int:pk>/delete/', views.ProductDeleteAPIView.as_view(),
          name='api_product_delete'),
     path('api/products/<int:pk>/', views.ProductDetailAPIView.as_view(),
          name='product_detail_api'),
     path('api/products/category/<int:category_id>/', views.products_by_category,
          name='products_by_category'),
     path('api/products/affordable/', views.affordable_products, name='affordable_products'),
     path('api/products/sorted/', views.sorted_products, name='sorted_products'),
     path('api/products/list/', views.ProductListView.as_view(), name='product_list'),
     path('api/products/average-price/', views.average_price, name='average_price'),
     path('api/login/', views.login_user, name='login'),
     path('api/members/me/', views.current_user, name='current_user'),
     path('api/products/top-rated/', views.top_rated_products, name='top_rated_products'),
     path('api/products/<int:pk>/recommend/', views.recommend_products,
          name='recommend_products'),
     path('api/products/special/rings-or-earrings/', views.rings_or_earrings_expensive),
     path('api/products/special/gold-or-silver-popular/', views.gold_or_silver_popular),

]

# Добавляем медиа-файлы только в режиме DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
