from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Cart, Product, CartItem

def add_to_cart(request, user_id, product_id):
    try:
        # Получаем корзину пользователя или создаем новую
        cart, created = Cart.objects.get_or_create(user_id=user_id)

        # Проверяем существование товара
        product = get_object_or_404(Product, pk=product_id)

        # Проверяем, есть ли товар уже в корзине
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            product_id=product,
            defaults={'quantity': 1}
        )

        if not item_created:
            # Если товар уже есть - увеличиваем количество
            cart_item.quantity += 1
            cart_item.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Товар добавлен в корзину',
            'cart_item_id': cart_item.id,
            'quantity': cart_item.quantity
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


def remove_from_cart(request, user_id, product_id):
    try:
        # Получаем корзину пользователя
        cart = get_object_or_404(Cart, user_id=user_id)

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


def update_cart_item_quantity(request, user_id, product_id):
    try:
        # Проверяем входные данные
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            raise ValueError("Количество не может быть меньше 1")

        # Получаем корзину и товар
        cart = get_object_or_404(Cart, user_id=user_id)
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)

        # Обновляем количество
        cart_item.quantity = quantity
        cart_item.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Количество обновлено',
            'quantity': cart_item.quantity,
        })

    except ValueError as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Ошибка обновления: {str(e)}'
        }, status=500)