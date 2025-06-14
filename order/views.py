import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import transaction
from django.utils.timezone import localtime, now, timedelta
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from .models import Order, OrderItem
from product.models import Product
from django.db.models.functions import TruncDate
from django.db.models import Count, Case, When, IntegerField

User = get_user_model()

# Формироване данных заказа -
def get_order_data(order_obj):
    user_data = {
        "full_name": order_obj.user.full_name,
        "phone": order_obj.user.phone,
        "email": order_obj.user.email,
        "address": order_obj.user.address if order_obj.user.address else None,
        "postal_code": order_obj.user.postal_code if order_obj.user.postal_code else None,
    }

    items_data = []
    for item in order_obj.items.all():
        product = item.product
        items_data.append({
            "product_id": product.id,
            "name": product.name,
            "quantity": item.quantity,
            "price": float(item.price_at_purchase)
        })

    return {
        "order_id": order_obj.id,
        "user": user_data,
        "items": items_data,
        "total_price": float(order_obj.total_price),
        "created_at": localtime(order_obj.created_at).isoformat(),
        "status": order_obj.status
    }

# Добавление нового заказа
@csrf_exempt
def create_order(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Для создания заказа необходимо авторизоваться."}, status=401)

        current_user = request.user

        try:
            body = json.loads(request.body)

            items = body.get("items")

            if not items:
                return JsonResponse({"error": "Необходимы items"}, status=400)

            if not current_user.address:
                return JsonResponse({
                    "error": "Пожалуйста, укажите адрес и почтовый индекс в профиле пользователя перед созданием заказа."},
                    status=400)

            total_price = 0
            order_items_data = []

            with transaction.atomic():
                for item_data in items:
                    product_id = item_data.get("product_id")
                    quantity = item_data.get("quantity")

                    if not product_id or not quantity:
                        return JsonResponse({"error": "В элементах заказа должны быть product_id и quantity"}, status=400)
                    if not isinstance(quantity, int) or quantity <= 0:
                        return JsonResponse({"error": "Количество товара должно быть положительным целым числом"}, status=400)

                    product = Product.objects.filter(id=product_id, is_deleted=False).first()
                    if not product:
                        return JsonResponse({"error": f"Товар с id {product_id} не найден или удалён"}, status=404)

                    if hasattr(product, 'stock_quantity') and product.stock_quantity < quantity:
                         return JsonResponse({"error": f"Недостаточно товара '{product.name}' на складе. Доступно: {product.stock_quantity}"}, status=400)

                    price = product.price * quantity
                    total_price += price
                    order_items_data.append({
                        "product": product,
                        "quantity": quantity,
                        "price": product.price
                    })

                # Создание заказа
                order = Order.objects.create(
                    user=current_user,
                    total_price=total_price,
                    status='В обработке'
                )

                # Создание элементов заказа
                for item in order_items_data:
                    OrderItem.objects.create(
                        order=order,
                        product=item["product"],
                        quantity=item["quantity"],
                        price_at_purchase=item["price"]
                    )

            return JsonResponse({"message": "Заказ успешно создан", "order_id": order.id}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Некорректный JSON формат запроса"}, status=400)
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except Product.DoesNotExist:
            return JsonResponse({"error": "Один или несколько продуктов не найдены."}, status=404)
        except Exception as e:
            return JsonResponse({"error": f"Произошла ошибка: {str(e)}"}, status=500)

    return JsonResponse({"error": "Только метод POST"}, status=405)


# Просмотр деталей заказа по его id
@csrf_exempt
def get_order_by_id(request, order_id):
    if request.method == "GET":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Для просмотра деталей заказа необходимо авторизоваться."}, status=401)

        try:
            order = Order.objects.select_related('user').prefetch_related('items__product').get(id=order_id)

            if not request.user.is_staff and order.user != request.user:
                return JsonResponse({"error": "У вас нет прав для просмотра этого заказа."}, status=403)

            data = get_order_data(order)
            return JsonResponse(data, safe=False)

        except Order.DoesNotExist:
            return JsonResponse({"error": "Заказ не найден"}, status=404)
        except Exception as e:
            return JsonResponse({"error": f"Произошла ошибка: {str(e)}"}, status=500)

    return JsonResponse({"error": "Только метод GET"}, status=405)

# Получение всех заказов с сортировкой, фильтрацией, поиском (только для админа)
@csrf_exempt
def get_all_orders(request):
    if request.method == "GET":
        # 1. Проверка авторизации и прав менеджера (is_staff):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Необходимо авторизоваться."}, status=401)
        if not request.user.is_staff:
            return JsonResponse({"error": "У вас нет прав для просмотра всех заказов."}, status=403)

        try:
            status_filter = request.GET.get("status")
            period_filter = request.GET.get("period")
            search = request.GET.get("search", "").strip()

            sort_by = request.GET.get("sort_by", "date")
            order_dir = request.GET.get("order", "desc")

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
                if search.isdigit(): # Если строка поиска - это число, ищем по ID заказа
                    orders = orders.filter(id=int(search))
                else: # Иначе ищем по email пользователя или полному имени
                    orders = orders.filter(
                        Q(user__email__icontains=search) |
                        Q(user__full_name__icontains=search)
                    )

            sort_fields = {
                "date": "created_at",
                "status": "status",
                "price": "total_price",
                "user": "user__email"
            }

            sort_field_name = sort_fields.get(sort_by, "created_at")
            if order_dir == "desc":
                sort_field_name = "-" + sort_field_name

            orders = orders.order_by(sort_field_name)

            result = []
            for order_obj in orders:
                result.append({
                    "order_id": order_obj.id,
                    "created_at": localtime(order_obj.created_at).isoformat(),
                    "user_username": order_obj.user.username,
                    "user_full_name": order_obj.user.full_name,
                    "total_price": float(order_obj.total_price),
                    "status": order_obj.status
                })

            return JsonResponse(result, safe=False)

        except Exception as e:
            return JsonResponse({"error": f"Произошла ошибка: {str(e)}"}, status=500)

    return JsonResponse({"error": "Только метод GET"}, status=405)


# Изменение статуса заказа (только для админа)
@csrf_exempt
def update_order_status(request, order_id):
    if request.method == "PATCH":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Необходимо авторизоваться."}, status=401)
        if not request.user.is_staff:
            return JsonResponse({"error": "У вас нет прав для изменения статуса заказа."}, status=403)

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

            return JsonResponse({"message": "Статус заказа успешно обновлен.", "order": get_order_data(order)}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Некорректный JSON формат запроса."}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Произошла ошибка: {str(e)}"}, status=500)

    return JsonResponse({"error": "Только метод PATCH"}, status=405)


# Получение всех заказов пользователя (конкретного user_id)
@csrf_exempt
def get_user_specific_orders(request, user_id):
    if request.method == "GET":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Необходимо авторизоваться для просмотра заказов."}, status=401)

        if not request.user.is_staff and request.user.id != user_id:
            return JsonResponse({"error": "У вас нет прав для просмотра заказов другого пользователя."}, status=403)

        try:
            target_user = User.objects.filter(id=user_id).first()
            if not target_user:
                return JsonResponse({"error": "Пользователь не найден."}, status=404)

            # prefetch_related для оптимизации
            orders = Order.objects.select_related("user").prefetch_related('items__product').filter(user=target_user).order_by('-created_at')

            result = []
            for order_obj in orders:
                result.append(get_order_data(order_obj))

            return JsonResponse(result, safe=False)

        except Exception as e:
            return JsonResponse({"error": f"Произошла ошибка: {str(e)}"}, status=500)

    return JsonResponse({"error": "Только метод GET"}, status=405)

@csrf_exempt
def get_order_stats(request):
    if request.method == "GET":
        if not request.user.is_authenticated or not request.user.is_staff:
            return JsonResponse({"error": "Недостаточно прав"}, status=403)

        try:
            # Статистика по статусам
            status_stats = Order.objects.values('status').annotate(
                count=Count('id'),
                total=Count('id', distinct=True)  # Убрана лишняя запятая
            )

            # Статистика по дням
            daily_stats = Order.objects.annotate(
                date=TruncDate('created_at')
            ).values('date').annotate(
                count=Count('id'),
                total_sum=Sum('total_price')
            ).order_by('-date')[:30]

            return JsonResponse({
                "status_stats": list(status_stats),
                "daily_stats": list(daily_stats)
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Только метод GET"}, status=405)