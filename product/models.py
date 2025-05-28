from django.db import models
from category.models import category
from brand.models import Brand

class Product(models.Model):
    brand_id = models.OneToOneField(Brand, on_delete=models.CASCADE)
    category_id = models.OneToOneField(category, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=100, null=False)  # модель часов
    price = models.FloatField(null=False)
    description = models.TextField(null=True)
    country = models.CharField(max_length=50, null=True)
    movement_type = models.CharField(max_length=50, null=True)
    caliber = models.CharField(max_length=20, null=True)
    case_material = models.CharField(max_length=50, null=True)
    dial_type = models.CharField(max_length=50, null=True)
    bracelet_material = models.CharField(max_length=50, null=True)
    water_resistance = models.CharField(max_length=50, null=True)
    glass_type = models.CharField(max_length=50, null=True)
    dimensions = models.CharField(max_length=50, null=True)
    is_deleted = models.BooleanField(default=False)


class ProductImage(models.Model):
    product_id = models.OneToOneField(Product, on_delete=models.SET_NULL, null=True)
    image_path = models.CharField(max_length=255, null=False)
    is_main = models.BooleanField(default=False)