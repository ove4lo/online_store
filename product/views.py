from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
from product.models import Product


def get_all_products(request):
    products = Product.objects.all()
    data = serializers.serialize('json', products)
    return JsonResponse(data, safe=False)