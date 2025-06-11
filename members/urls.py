# 
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.views.generic import TemplateView
import debug_toolbar
from django.urls import include

urlpatterns = [
    # Сначала API
    path('', views.home, name='home'),
    path('api/products/latest/', views.latest_products, name='latest_products'),
    path('api/products/create/', views.ProductCreateAPIView.as_view(), name='product_create'),
    path('api/products/<int:pk>/update/', views.ProductUpdateAPIView.as_view(), name='product_update'),
    path('api/products/<int:pk>/delete/', views.ProductDeleteAPIView.as_view(), name='product_delete'),
    path('api/products/<int:pk>/', views.product_detail, name='product_detail_view'),
    
    path('catalog/', views.catalog, name='catalog'),
    path('members-page/', views.members_page, name='members_page'),
    path('api/products/category/<int:category_id>/', views.products_by_category, name='products_by_category'),
    path('api/products/affordable/', views.affordable_products, name='affordable_products'),
    path('api/products/sorted/', views.sorted_products, name='sorted_products'),
    path('api/products/list/', views.ProductListView.as_view(), name='product_list'),
    path('api/products/average-price/', views.average_price, name='average_price'),
    path('api/register/', views.register, name='register'),
    path('api/login/', views.login_user, name='login'),
    path('api/members/me/', views.current_user, name='current_user'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]