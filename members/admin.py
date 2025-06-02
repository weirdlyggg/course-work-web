from django.contrib import admin
from .models import User, Category, Product, Favorite, ProductImg, Order, OrderItem, Review, ReviewImg, Gemestone, ProductGemestone

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
    list_display = ('name', 'price', 'category',)
    search_fields = ('name',)
    list_filter = ('category',)
    inlines = [ProductGemstoneInLine, ProductImageInLine]

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'product',)
    search_fields = ('user__email', 'product__name')

@admin.register(ProductImg)
class ProductImgAdmin(admin.ModelAdmin):
    list_display = ('product', 'img',)
    search_fields = ('product__name',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_price', 'status', 'created_at',)
    search_fields = ('user__email',)
    list_filter = ('user',)

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