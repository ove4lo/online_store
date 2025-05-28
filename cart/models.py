from django.db import models
from User.models import User
from product.models import Product


class Cart(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product_id = models.OneToOneField(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)