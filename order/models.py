from django.db import models
from product.models import Product
from User.models import User


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='pending')
    total_price = models.FloatField()
    order_number = models.CharField(max_length=20, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['user']
        db_table = 'order'
        indexes = [
            models.Index(fields=['user']),
        ]


class OrderItem(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_id = models.OneToOneField(Product, on_delete=models.CASCADE)
    quantity = models.FloatField(null=False)
    price_at_purchase = models.FloatField(null=False)

    class Meta:
        ordering = ['order_id']
        db_table = 'order_item'
        indexes = [
            models.Index(fields=['order_id']),
        ]

class UserAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255, null=False)
    city = models.CharField(max_length=50, null=False)
    postal_code = models.CharField(max_length=20, null=False)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ['user']
        db_table = 'user_address'
        indexes = [
            models.Index(fields=['user']),
        ]
