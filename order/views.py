import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Order, OrderItem, Product
from User.models import User
from django.utils.timezone import localtime
from django.utils.timezone import now, timedelta
from django.db.models import Q

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

# Просмотр деталей заказа по его id
@csrf_exempt
def get_order_by_id(request, order_id):
    if request.method == "GET":
        try:
            order = Order.objects.select_related('user').prefetch_related('orderitem_set__product_id').get(id=order_id)

            # Данные пользователя
            user = order.user
            user_data = {
                "full_name": user.full_name,
                "phone": user.phone,
                "email": user.email,
                "address": order.address
            }

            # Товары в заказе
            items_data = []
            for item in order.orderitem_set.all():
                product = item.product_id
                items_data.append({
                    "name": product.name,
                    "quantity": item.quantity,
                    "price": float(item.price_at_purchase)
                })

            data = {
                "user": user_data,
                "items": items_data,
                "total_price": float(order.total_price),
                "created_at": localtime(order.created_at).strftime("%Y-%m-%d %H:%M:%S"),
                "status": order.status
            }

            return JsonResponse(data, safe=False)

        except Order.DoesNotExist:
            return JsonResponse({"error": "Заказ не найден"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Только метод GET"}, status=405)

# Получение всех заказов с сортировкой, фильтрацией, поиском
@csrf_exempt
def get_all_orders(request):
    if request.method == "GET":
        try:
            status_filter = request.GET.get("status")
            period_filter = request.GET.get("period")
            search = request.GET.get("search", "").strip().lower()

            sort_by = request.GET.get("sort_by", "date")  # date, status, price, user
            order = request.GET.get("order", "desc")

            orders = Order.objects.select_related("user").all()

            if status_filter:
                orders = orders.filter(status__iexact=status_filter)

            if period_filter:
                today = now().date()
                if period_filter == "today":
                    orders = orders.filter(created_at__date=today)
                elif period_filter == "week":
                    week_ago = today - timedelta(days=7)
                    orders = orders.filter(created_at__date__gte=week_ago)
                elif period_filter == "month":
                    month_ago = today - timedelta(days=30)
                    orders = orders.filter(created_at__date__gte=month_ago)

            if search:
                if search.isdigit():
                    orders = orders.filter(id=int(search))
                else:
                    orders = orders.filter(user__email__icontains=search)

            sort_fields = {
                "date": "created_at",
                "status": "status",
                "price": "total_price",
                "user": "user__email"
            }

            sort_field = sort_fields.get(sort_by, "created_at")
            if order == "desc":
                sort_field = "-" + sort_field

            orders = orders.order_by(sort_field)

            result = []
            for order in orders:
                user = order.user.full_name or order.user.email
                result.append({
                    "order_id": order.id,
                    "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "user": user,
                    "total_price": float(order.total_price),
                    "status": order.status
                })

            return JsonResponse(result, safe=False)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Только метод GET"}, status=405)

# Изменение у заказа его статус
@csrf_exempt
def update_order_status(request, order_id):
    if request.method == "PATCH":
        try:
            body = json.loads(request.body)
            new_status = body.get("status")

            allowed_statuses = ["В обработке", "Отправлен", "Доставлен", "Отменен"]
            if new_status not in allowed_statuses:
                return JsonResponse({"error": "Недопустимый статус"}, status=400)

            order = Order.objects.filter(id=order_id).first()
            if not order:
                return JsonResponse({"error": "Заказ не найден"}, status=404)

            order.status = new_status
            order.save()

            return JsonResponse({"message": "Статус обновлен", "order_id": order.id, "new_status": order.status})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Только метод PATCH"}, status=405)