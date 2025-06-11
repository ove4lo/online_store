# wishlist/models.py
from django.db import models
from django.conf import settings
from product.models import Product

class Wishlist(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        # Теперь order_by ['user'] вместо ['user_id']
        ordering = ['user']
        db_table = 'wishlist'

    def __str__(self):
        return f"Wishlist for {self.user.username}"