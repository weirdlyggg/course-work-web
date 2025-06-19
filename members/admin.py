from django.contrib import admin, messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from .models import User, Category, Product, Favorite, ProductImg, Order, OrderItem, Review, ReviewImg, Gemestone, ProductGemestone
from .models import Document, Video, SaleEvent

@admin.action(description="Отметить выбранные заказы как отправленные")
def mark_as_shipped(modeladmin, request, queryset):
    updated = queryset.update(status='shipped')  # массовый UPDATE
    messages.success(request, f"{updated} заказ(ов) отмечены как Shipped.")

@admin.action(description="Удалить отмененные заказы")
def delete_cancelled(modeladmin, request, queryset):
    # удаляем только те, у которых status='cancelled'
    to_delete = queryset.filter(status='cancelled')
    count = to_delete.count()
    to_delete.delete()  # массовый DELETE
    messages.success(request, f"{count} отмененных заказ(ов) удалены.")

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'created_at')
    search_fields = ('title',)

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):  
    list_display = ('title', 'file')

class ProductInLine(admin.TabularInline):
    model = Product
    extra = 0

class ReviewInLine(admin.TabularInline):
    model = Review
    extra = 0

class OrderItemInLine(admin.TabularInline):
    model = OrderItem
    extra = 0

class ProductGemstoneInLine(admin.TabularInline):
    model = ProductGemestone
    extra = 0
    can_delete = True

class ProductImageInLine(admin.TabularInline):
    model = ProductImg
    extra = 0
    can_delete = True

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_joined',)
    search_fields = ('first_name', 'last_name', 'email',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'view_count',)
    search_fields = ('name',)
    list_filter = ('category',)
    inlines = [ProductGemstoneInLine, ProductImageInLine]

@admin.register(SaleEvent)
class SaleEventAdmin(admin.ModelAdmin):
    list_display = ('category', 'discount', 'end_time')
    list_filter  = ('category',)
    ordering     = ('-end_time',)

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'product',)
    search_fields = ('user__email', 'product__name')

@admin.register(ProductImg)
class ProductImgAdmin(admin.ModelAdmin):
    list_display = ('product', 'img',)
    search_fields = ('product__name',)

@admin.action(description="Скачать заказ в PDF")
def export_order_to_pdf(modeladmin, request, queryset):
    for order in queryset:
        html = render_to_string("pdf/order.html", {"order": order})
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="order_{order.id}.pdf"'
        pisa.CreatePDF(html, dest=response)
        return response

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_price', 'status', 'created_at',)
    search_fields = ('user__email',)
    list_filter = ('user',)
    actions = [export_order_to_pdf, mark_as_shipped, delete_cancelled]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'prise_at_time_of_purchase',)
    search_fields = ('order__id', 'product__name',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'created_at',)
    search_fields = ('product__name', 'user__email',)

@admin.register(ReviewImg)
class ReviewImgAdmin(admin.ModelAdmin):
    list_display = ('review', 'img',)
    search_fields = ('review__product__name',)

@admin.register(Gemestone)
class GemestoneAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(ProductGemestone)
class ProductGemestoneAdmin(admin.ModelAdmin):
    list_display = ('product', 'gemestone')

