from django.db import models
from django.utils.text import slugify
from django.conf import settings

# Create your models here.
class Base(models.Model):
    company = models.CharField(max_length=50)
    footer = models.CharField(max_length=200)
    x = models.URLField()
    ln = models.URLField()
    ig = models.URLField()
    yt = models.URLField()

    def __str__(self):
        return self.company
    

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    image = models.URLField(blank=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='product')
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='product', blank=True, null=True)
    rating = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.IntegerField()
    description = models.CharField(max_length=200, blank=True)
    price_now = models.IntegerField()
    price_was = models.IntegerField()
    save_perc = models.IntegerField()
    is_featured = models.BooleanField(default=False)

    def save(self, *args, **kwargs):                          
            if not self.slug:
                self.slug = slugify(self.name)
            super().save(*args, **kwargs)
    
    def __str__(self):                                  
            return self.name


class Messageform(models.Model):
    SUBJECT_CHOICES = [
        ('order', 'Order — tracking, change, or cancellation'),
        ('returns', 'Returns or refunds'),
        ('warranty', 'Warranty claim or product issue'),
        ('trade', 'Trade / wholesale inquiry'),
        ('press', 'Press, partnership, or affiliate'),
        ('other', 'Something else'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    subject = models.CharField(max_length=100, choices=SUBJECT_CHOICES, default='other')
    order_number = models.CharField(max_length=50, blank=True)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class Contact(models.Model):
    email = models.EmailField(max_length=100)
    phone = models.BigIntegerField()
    live_chat = models.CharField(max_length=50)
    address = models.CharField(max_length=100)

    def __str__(self):
        return self.email

class FAQ(models.Model):
    question = models.CharField(max_length=100)
    answer = models.CharField(max_length=400)

    def __str__(self):
        return self.answer

class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f'{self.user.email} — {self.product.name} x{self.quantity}'

    @property
    def subtotal(self):
        return self.product.price_now * self.quantity


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Order #{self.id} — {self.user.email}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveBigIntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.product.name} x{self.quantity}'

    @property
    def subtotal(self):
        return self.price_at_purchase * self.quantity


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email