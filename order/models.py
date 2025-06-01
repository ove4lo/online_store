from django.db import models
from product.models import Product
from User.models import User


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)

    status = models.CharField(max_length=20, default='В обработке')
    total_price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['user']
        db_table = 'order'
        indexes = [
            models.Index(fields=['user']),
        ]


class OrderItem(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price_at_purchase = models.FloatField()

    class Meta:
        ordering = ['order_id']
        db_table = 'order_item'
        indexes = [
            models.Index(fields=['order_id']),
        ]
