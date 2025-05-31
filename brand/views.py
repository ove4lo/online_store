from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
from product.models import Product
import json
from django.http import JsonResponse
from .models import Brand
from brand.models import Brand

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


# Получение всех брендов
def get_all_brands(request):
    brands = Brand.objects.all()
    data = []

    for brand in brands:
        data.append({
            "id": brand.id,
            "name": brand.name,
            "description": brand.description
        })
    return JsonResponse(data, safe=False)


# Создание бренда
@csrf_exempt
def create_brand(request):
    if request.method == "POST":
        try:
            brand = Brand.objects.create(
                name=request.POST["name"],
                description=request.POST["description"],
            )
            return JsonResponse({'message': 'сreation is successful'}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": 'only method POST'}, status=405)


# Обновление бренда
@csrf_exempt
def update_brand(request, id):
    pass


# удаление бренда
@csrf_exempt
def delete_brand(request, id):
    try:
        if request.method == "DELETE":
            brand = Brand.objects.get(id=id)
            brand.delete()
            return JsonResponse({'message': 'brand removed'})
    except Brand.DoesNotExist:
        return JsonResponse({"error": "brand is not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=405)
