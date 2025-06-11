from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
import json

from django.views.decorators.csrf import csrf_exempt

from product.models import Product
from .models import Wishlist


def get_wishlist(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 'error',
            'message': 'Требуется авторизация'
        }, status=401)

    if request.method != 'GET':
        return JsonResponse({
            'status': 'error',
            'message': 'Метод не разрешен'
        }, status=405)

    try:
        wishlist_items = Wishlist.objects.filter(user=request.user)
        wishlist_data = [{
            'product_id': item.product.id,
            'product_name': item.product.name,
            'brand': item.product.brand.name,
            'category': item.product.category.name,
            'price': item.product.price,
            'description': item.product.description,
            'country': item.product.country,
            'movement_type': item.product.movement_type,
            'caliber': item.product.caliber,
            'case_material': item.product.case_material,
            'dial_type': item.product.dial_type,
            'bracelet_material': item.product.bracelet_material,
            'water_resistance': item.product.water_resistance,
            'glass_type': item.product.glass_type,
            'dimensions': item.product.dimensions,

        } for item in wishlist_items]

        return JsonResponse({
            'status': 'success',
            'wishlist': wishlist_data
        }, status=200)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
def remove_from_wishlist(request, product_id):
    """
    Удаление продукта из избранного
    """
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 'error',
            'message': 'Требуется авторизация'
        }, status=401)

    if request.method != 'DELETE':
        return JsonResponse({
            'status': 'error',
            'message': 'Метод не разрешен'
        }, status=405)

    try:
        product = Product.objects.get(id=product_id)
        wishlist_item = Wishlist.objects.get(user=request.user, product=product)
        wishlist_item.delete()

        return JsonResponse({
            'status': 'success',
            'message': 'Продукт удален из избранного'
        }, status=200)

    except ObjectDoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Продукт не найден в избранном'
        }, status=404)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': 'Не удалось удалить продукт из избранного'
        }, status=500)

@csrf_exempt
def add_to_wishlist(request):
    """
    Добавление продукта в избранное
    """
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 'error',
            'message': 'Требуется авторизация'
        }, status=401)

    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Метод не разрешен'
        }, status=405)

    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')

        if not product_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Не указан ID продукта'
            }, status=400)

        product = Product.objects.get(id=product_id)

        if Wishlist.objects.filter(user=request.user, product=product).exists():
            return JsonResponse({
                'status': 'error',
                'message': 'Продукт уже в избранном'
            }, status=400)

        Wishlist.objects.create(user=request.user, product=product)

        return JsonResponse({
            'status': 'success',
            'message': 'Продукт добавлен в избранное'
        }, status=201)

    except Product.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Продукт не найден'
        }, status=404)

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Неверный формат данных'
        }, status=400)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': 'Не удалось добавить продукт в избранное'
        }, status=500)