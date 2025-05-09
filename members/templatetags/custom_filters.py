from django import template
from ..models import Product

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    return value * arg  # Умножение значения на аргумент

@register.filter(name='uppercase_words')
def uppercase_words(value):
    return ' '.join(word.upper() for word in value.split())  # Преобразование слов в верхний регистр

@register.simple_tag(name='say_hello')
def say_hello():
    return "Hello, World!"

@register.simple_tag(takes_context=True)
def greet_user(context):
    user = context['request'].user
    return f"Hello, {user.username}!" if user.is_authenticated else "Hello, Guest!"

@register.inclusion_tag('tags/product_list.html')
def show_products():
    products = Product.objects.all()[:5]  # Первые 5 товаров
    return {'products': products}