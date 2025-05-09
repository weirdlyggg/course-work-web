from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.views.generic import TemplateView

urlpatterns = [
    path('', RedirectView.as_view(url='/react-app/', permanent=False), name='root'),
    path('react-app/', TemplateView.as_view(template_name='index.html'), name='react_app'),
    # Список пользователей
    path('api/members/', views.members, name='members'),

    # Товары по категории
    path('api/products/category/<int:category_id>/', views.products_by_category, name='products_by_category'),

    # Исключение дорогих товаров
    path('api/products/affordable/', views.affordable_products, name='affordable_products'),

    # Сортировка товаров
    path('api/products/sorted/', views.sorted_products, name='sorted_products'),

    # Детали товара
    path('api/product/<int:product_id>/', views.product_detail, name='product_detail'),

    # Пагинация товаров
    path('api/products/list/', views.ProductListView.as_view(), name='product_list'),

    # Средняя цена товаров
    path('api/products/average-price/', views.average_price, name='average_price'),

    # Регистрация пользователя
    path('api/register/', views.register, name='register'),

    # Маршрут для логина
    path('api/login/', views.login_user, name='login'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)