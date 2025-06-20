# members/forms.py

from django import forms
from .models import Product, User  # Теперь User доступен

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # Явно берем поля (можно было exclude=['status'] и т.п.)
        fields = ['name', 'description', 'price', 'category']
        
        labels = {
            'name': 'Название товара',
            'description': 'Описание',
            'price': 'Цена (₽)',
            'category': 'Категория',
        }
        
        help_texts = {
            'name': 'Краткое, до 255 символов.',
            'price': 'Число без пробелов.',
        }
        
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        
        error_messages = {
            'name': {
                'required': 'Название обязательно.',
                'max_length': 'Слишком длинное название (не более 255 символов).',
            },
            'price': {
                'invalid': 'Введите корректное число.',
                'required': 'Цена обязательна.',
            },
        }
        css = {
            'all': (
                'css/product_form.css',  # файл в static/css/
            )
        }
        js = (
            'js/product_form.js',    # файл в static/js/
        )

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is None or price <= 0:
            raise forms.ValidationError("Цена должна быть положительной.")
        return price
    
    def clean_description(self):
        desc = self.cleaned_data.get('description') or ""
        if len(desc.strip()) < 20:
            raise forms.ValidationError(
                "Описание слишком короткое — минимум 20 символов."
            )
        return desc


# Форма редактирования профиля пользователя
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'address']

from django import forms
from .models import User

class CustomUserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'phone_number', 'address']

    def save(self, commit=True):
        # 1) создаём объект, но ещё НЕ сохраняем в БД
        user = super().save(commit=False)
        # 2) хешируем пароль
        user.set_password(self.cleaned_data['password'])
        # 3) если commit=True, сохраняем; иначе вернём незаписанный объект
        if commit:
            user.save()
        return user

from .models import Review

class OrderReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'min': 1, 'max': 5,
                'class': 'form-control',
                'placeholder': '1–5'
            }),
            'text': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Ваш комментарий'
            }),
        }
        labels = {
            'rating': 'Оценка (1–5)',
            'text': 'Комментарий',
        }
        help_texts = {
            'rating': 'Введите число от 1 до 5',
        }
