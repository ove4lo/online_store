from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
from product.models import Product
import json
from django.http import JsonResponse
from .models import Brand
from brand.models import Brand
from category.models import category
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


def get_all_brands(request):
    brands = Brand.objects.all()
    data = serializers.serialize('json', brands)
    print('ewqewq')
    return JsonResponse(data, safe=False)