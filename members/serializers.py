from rest_framework import serializers
# pylint: disable=no-member

from .models import (
User,
Product,
Category,
Review,
Order,
ProductImg,
SaleEvent
)

# Сериализатор для модели User
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_staff']

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Используем User.objects.create_user
        return User.objects.create_user(**validated_data)

# # Сериализатор для модели Product
# class ProductSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Product
#         fields = ['id', 'name', 'description', 'price', 'category']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Рейтинг от 1 до 5")
        return value
    class Meta:
        model = Review
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class ProductImgSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImg
        fields = ['img']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImgSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'images']

class SaleEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleEvent
        fields = '__all__'

    def validate_discount(self, value):
        if not (1 <= value < 100):
            raise serializers.ValidationError('Скидка должна быть от 1 до 99 процентов.')
        return value
