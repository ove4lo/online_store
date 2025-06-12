from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import json
from .models import Cart, CartItem, Product


# вроде работает, а вроде и нет
@csrf_exempt
@require_POST
def add_to_cart(request):
    try:
        if not request.user.is_authenticated:
            return JsonResponse({
                'status': 'error',
                'message': 'Требуется авторизация'
            }, status=401)

        data = json.loads(request.body)
        product_id = data.get('product_id')

        if not product_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Необходимо указать product_id'
            }, status=400)

        # Получаем корзину пользователя или создаем новую
        cart, created = Cart.objects.get_or_create(user=request.user)  # Используем request.user вместо user_id

        # Проверяем существование товара
        product = get_object_or_404(Product, pk=product_id)

        # Добавляем товар в корзину
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 1}
        )

        # if not item_created:
        #     cart_item.quantity += 1
        #     cart_item.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Товар добавлен в корзину',
            'cart_item_id': cart_item.id,
            'quantity': cart_item.quantity
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Неверный формат JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


# удаление товара из корзины
@csrf_exempt
def remove_from_cart(request, product_id):
    try:
        if request.method == "DELETE":
            # Получаем корзину пользователя

            cart = get_object_or_404(Cart, user=request.user)

            # Находим и удаляем конкретный товар в корзине
            cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
            cart_item.delete()

            return JsonResponse({
                'status': 'success',
                'message': 'Товар удален из корзины',
            })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


# обновление количества товара из корзины
@csrf_exempt
def update_cart_item_quantity(request):
    try:
        if not request.user.is_authenticated:
            return JsonResponse({
                'status': 'error',
                'message': 'Требуется авторизация'
            }, status=401)

        data = json.loads(request.body)
        product_id = data.get('product_id')
        action = data.get('action')

        # Получаем корзину и товар
        cart = get_object_or_404(Cart, user=request.user)
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
        if action == '+':
            cart_item.quantity += 1
        elif action == '-':
            cart_item.quantity -= 1
        cart_item.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Количество увеличено на 1',
            'quantity': cart_item.quantity,
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Ошибка обновления: {str(e)}'
        }, status=500)

# получение корзины

def get_cart(request):
    try:
        if not request.user.is_authenticated:
            return JsonResponse({
                'status': 'error',
                'message': 'Требуется авторизация'
            }, status=401)

        # Получаем корзину пользователя
        cart = get_object_or_404(Cart, user=request.user)  # Используем request.user

        # Получаем товары в корзине
        cart_items = CartItem.objects.filter(cart=cart)

        data = []
        for item in cart_items:
            try:
                product = Product.objects.get(id=item.product_id, is_deleted=False)
                data.append({
                    'product_id': item.product_id,
                    'quantity': item.quantity,
                    'brand_id': product.brand.name,
                    'name': product.name,
                    'price': product.price,
                    'description': product.description,
                    'movement_type': product.movement_type,
                    'caliber': product.caliber,
                    'case_material': product.case_material,
                    'dial_type': product.dial_type,
                    'bracelet_material': product.bracelet_material,
                    'water_resistance': product.water_resistance,
                    'glass_type': product.glass_type,
                    'dimensions': product.dimensions,
                })
            except Product.DoesNotExist:
                continue

        return JsonResponse({'data': data}, status=200)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
