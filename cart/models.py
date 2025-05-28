from django.db import models

from product.models import Product


class Cart(models.Model):
    #user_id = models.IntegerField()
    pass

class CartItem(models.Model):
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    product_id = models.OneToOneField(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)