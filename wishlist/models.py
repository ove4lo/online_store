from django.db import models
from django.contrib.auth.models import User

from product.models import Product


class Wishlist(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
