from django.db import models

class User(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=11)
    password = models.CharField(max_length=255)
    address = models.TextField()
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
class Favorite(models.Model):
    user = models.ForeignKey(User, related_name='favorites', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='favorites', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} favorited by {self.product}"
    
class ProductImg(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    img = models.ImageField(upload_to='product_images/', null=True, blank=True)

    def __str__(self):
        return f"Image for {self.product.name}"
    
class Order(models.Model):
    user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.first_name} {self.user.last_name}"
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    prise_at_time_of_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} {self.quantity}"
    
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.product.name} by {self.user.first_name} {self.user.last_name}"
    
class ReviewImg(models.Model):
    review = models.ForeignKey(Review, related_name='images', on_delete=models.CASCADE)
    img = models.ImageField(upload_to='review_images/', null=True, blank=True)

    def __str__(self):
        return f"Image for review {self.review.id}"
    
class Gemestone(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
  
class ProductGemestone(models.Model):
    product = models.ForeignKey(Product, related_name='gemestones', on_delete=models.CASCADE)
    gemestone = models.ForeignKey(Gemestone, related_name='products', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product.name} with {self.gemestone.name}"