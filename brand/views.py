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
def get_all_brands(request) -> JsonResponse:
    """Метод получения всех брендов"""
    try:
        brands = Brand.objects.all()
        data = []
        for brand in brands:
            data.append({
                "id": brand.id,
                "name": brand.name,
                "description": brand.description
            })
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, safe=False)


# Создание бренда
@csrf_exempt
def create_brand(request) -> JsonResponse:
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            brand = Brand.objects.create(
                name=data["name"],
                description=data["description"],
            )
            return JsonResponse({'message': 'сreation is successful'}, status=201)

        except Exception as e:
            return JsonResponse({"ТУТ": str(e)}, status=500)
    return JsonResponse({"error": 'only method POST'}, status=405)


# Обновление бренда
@csrf_exempt
def update_brand(request, id) -> JsonResponse:
    try:
        brand = Brand.objects.get(id=id)
    except Brand.DoesNotExist:
        return JsonResponse({'message': 'Brand does not exist'}, status=404)
    if request.method == "PATCH":
        try:
            brand.name = request.POST["name"]
            brand.description = request.POST["description"]
            brand.save()
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    else:
        return JsonResponse({"error": 'only method PATCH'}, status=405)
    return JsonResponse({"message": 'update successful'}, status=200)


# удаление бренда
@csrf_exempt
def delete_brand(request, id) -> JsonResponse:
    try:
        if request.method == "DELETE":
            brand = Brand.objects.get(id=id)
            brand.delete()
            return JsonResponse({'message': 'brand removed'}, status=204)
    except Brand.DoesNotExist:
        return JsonResponse({"error": "brand is not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=405)
