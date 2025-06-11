from django.db import models
from category.models import category
from brand.models import Brand

class Product(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    category = models.ManyToManyField(category, related_name='products')

    name = models.CharField(max_length=100, null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    description = models.TextField(null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    movement_type = models.CharField(max_length=50, null=True, blank=True)
    caliber = models.CharField(max_length=20, null=True, blank=True)
    case_material = models.CharField(max_length=50, null=True, blank=True)
    dial_type = models.CharField(max_length=50, null=True, blank=True)
    bracelet_material = models.CharField(max_length=50, null=True, blank=True)
    water_resistance = models.CharField(max_length=50, null=True, blank=True)
    glass_type = models.CharField(max_length=50, null=True, blank=True)
    dimensions = models.CharField(max_length=50, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']
        db_table = 'product'
        indexes = [
            models.Index(fields=['brand']),
            models.Index(fields=['name']),
            models.Index(fields=['is_deleted']),
        ]

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', null=True, blank=True)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    is_main = models.BooleanField(default=False)

    class Meta:
        ordering = ['product', '-is_main']
        db_table = 'product_image'

    def __str__(self):
        return f"Image for {self.product.name if self.product else 'No Product'} (Main: {self.is_main})"