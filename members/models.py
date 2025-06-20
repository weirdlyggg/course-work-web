from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from simple_history.models import HistoricalRecords


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email должен быть указан')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields['is_staff']:
            raise ValueError('Superuser must have is_staff=True.')

        if not extra_fields['is_superuser']:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)
    
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=11, null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.email
    
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
    
class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

class SaleEvent(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория распродажи")
    discount = models.PositiveIntegerField(verbose_name="Скидка, %")
    end_time = models.DateTimeField(verbose_name="Конец акции")

    def clean(self):
        super().clean()
        if not (1 <= self.discount < 100):
            raise ValidationError({
                'discount': 'Скидка должна быть от 1% до 99%.'
            })

    def __str__(self):
        return f"Распродажа: {self.category.name} –{self.discount}% до {self.end_time}"

    class Meta:
        verbose_name = "Событие распродажи"
        verbose_name_plural = "События распродаж"

class AvailableProductsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='available')

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default='available')
    view_count = models.PositiveIntegerField(default=0, verbose_name="Просмотров")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата добавления")

    objects = models.Manager()
    available = AvailableProductsManager()
    history = HistoricalRecords()

    def clean(self):
        super().clean()
        if self.price <= 0:
            raise ValidationError({
                'price': 'Цена должна быть больше нуля.'
            })

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-price']

    def get_absolute_url(self):
        return reverse('product-detail', args=[str(self.id)])
    
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    @property
    def discounted_price(self):
        """
        Если в категории продукта есть активное событие распродажи,
        возвращаем новую цену, иначе — None.
        """
        now = timezone.now()
        event = SaleEvent.objects.filter(
            category=self.category,
            end_time__gt=now
        ).first()
        if not event:
            return None
        return self.price * (100 - event.discount) / 100

    
class Favorite(models.Model):
    user = models.ForeignKey(User, related_name='favorites', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='favorites', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} favorited by {self.product}"
    
    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"
    
class ProductImg(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    img = models.ImageField(upload_to='product_images/', null=True, blank=True)

    def __str__(self):
        return f"Image for {self.product.name}"
    
    class Meta:
        verbose_name = "Фото товара"
        verbose_name_plural = "Фото товаров"
    
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)

    history = HistoricalRecords()

    def __str__(self):
        return f"Order #{self.id} by {self.user.first_name} {self.user.last_name}"
    
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    prise_at_time_of_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} {self.quantity}"
    
    class Meta:
        verbose_name = "Товар в заказе"
        verbose_name_plural = "Товары в заказе"
    
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def clean(self):
        super().clean()
        if not (1 <= self.rating <= 5):
            raise ValidationError({
                'rating': 'Оценка должна быть в диапазоне от 1 до 5.'
            })

    def __str__(self):
        return f"Review for {self.product.name} by {self.user.first_name} {self.user.last_name}"
    class Meta:
        ordering = ['-created_at']

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
    
class ReviewImg(models.Model):
    review = models.ForeignKey(Review, related_name='images', on_delete=models.CASCADE)
    img = models.ImageField(upload_to='review_images/', null=True, blank=True)

    def __str__(self):
        return f"Image for review {self.review.id}"
    
    class Meta:
        verbose_name = "Фото отзыва"
        verbose_name_plural = "Фото отзывов"

class Gemestone(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Камень"
        verbose_name_plural = "Камни"
  
class ProductGemestone(models.Model):
    product = models.ForeignKey(Product, related_name='gemestones', on_delete=models.CASCADE)
    gemestone = models.ForeignKey(Gemestone, related_name='products', on_delete=models.CASCADE, null=True, blank=True)

    def clean(self):
        if self.gemestone is None:
            raise ValidationError("Выберите камень для украшения")

    def __str__(self):
        return f"{self.product.name} with {self.gemestone.name}"
    
    class Meta:
        verbose_name = "ТоварКамень"
        verbose_name_plural = "ТоварыКамни"

class Document(models.Model):
    title = models.CharField(max_length=255)
    name = models.CharField("Название", max_length=255)
    file = models.FileField("Файл", upload_to="docs/")

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"

    def save(self, *args, **kwargs):
        print(f"[Document.save] Сохраняем документ: {self.title}")
        # вызываем родительский метод, чтобы файл и запись в БД сохранились
        super().save(*args, **kwargs)
        # логика после сохранения (опционально)
        print(f"[Document.save] Документ {self.pk} сохранён.")

class Video(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название видео")
    url = models.URLField(verbose_name="Ссылка на видео")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Добавлено")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Видео"
        verbose_name_plural = "Видео"
