import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Order, OrderItem, Product
from User.models import User

# Добавление нового заказа
@csrf_exempt
def create_order(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)

            user_id = body.get("user_id")
            items = body.get("items")
            address = body.get("address")
            postal_code = body.get("postal_code")

            # Проверка обязательных полей
            if not user_id or not items or not address or not postal_code:
                return JsonResponse({"error": "Необходимы user_id, items, address, city, postal_code"}, status=400)

            # Проверка существования пользователя
            user = User.objects.filter(id=user_id).first()
            if not user:
                return JsonResponse({"error": "Пользователь не найден"}, status=404)

            total_price = 0
            order_items = []

            for item in items:
                product_id = item.get("product_id")
                quantity = item.get("quantity")

                if not product_id or not quantity:
                    return JsonResponse({"error": "Нет product_id и quantity"}, status=400)

                product = Product.objects.filter(id=product_id, is_deleted=False).first()
                if not product:
                    return JsonResponse({"error": f"Товар с id {product_id} не найден или удалён"}, status=404)

                price = product.price * quantity
                total_price += price
                order_items.append({
                    "product": product,
                    "quantity": quantity,
                    "price": product.price
                })

            # Создание заказа
            order = Order.objects.create(
                user=user,
                address=address,
                postal_code=postal_code,
                total_price=total_price,
                status='В обработке'
            )

            # Создание элементов заказа
            for item in order_items:
                OrderItem.objects.create(
                    order_id=order,
                    product_id=item["product"],
                    quantity=item["quantity"],
                    price_at_purchase=item["price"]
                )

            return JsonResponse({"message": "Заказ успешно создан", "order_id": order.id}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Только метод POST"}, status=405)
