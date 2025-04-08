from django.contrib import admin
from .models import User, Category, Product, Favorite, ProductImg, Order, OrderItem, Review, ReviewImg, Gamestone, ProductGamestone

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_joined',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category',)

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'product',)

@admin.register(ProductImg)
class ProductImgAdmin(admin.ModelAdmin):
    list_display = ('product', 'imgurl',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_price', 'status', 'created_at',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'prise_at_time_of_purchase',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'created_at',)

@admin.register(ReviewImg)
class ReviewImgAdmin(admin.ModelAdmin):
    list_display = ('review', 'imgurl',)

@admin.register(Gamestone)
class GamestoneAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(ProductGamestone)
class ProductGamestoneAdmin(admin.ModelAdmin):
    list_display = ('product', 'gamestone')