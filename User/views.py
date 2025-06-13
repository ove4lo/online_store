import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db import transaction
from cart.models import Cart

User = get_user_model()


# Формирование данных пользователя в JSON-ответе
def get_user_data(user):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "phone": user.phone,
        "address": user.address if user.address else None,
        "postal_code": user.postal_code if user.postal_code else None,
        "is_staff": user.is_staff,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
    }


# Регистрация нового пользователя
@csrf_exempt
def register_user(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)

            username = body.get("username")
            email = body.get("email")
            password = body.get("password")
            full_name = body.get("full_name")
            phone = body.get("phone")
            address = body.get("address", "")  # Опционально
            postal_code = body.get("postal_code", "")  # Опционально

            if not all([username, email, password, full_name, phone]):
                return JsonResponse(
                    {"error": "Не заполнены обязательные поля: username, email, password, full_name, phone"},
                    status=400)

            if "@" not in email or "." not in email:
                return JsonResponse({"error": "Некорректный формат email"}, status=400)

            if len(password) < 8:
                return JsonResponse({"error": "Пароль должен быть не менее 8 символов."}, status=400)

            with transaction.atomic():
                try:
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        full_name=full_name,
                        phone=phone,
                        address=address,
                        postal_code=postal_code
                    )
                    cart = Cart.objects.create(user=user)
                    login(request, user)

                    return JsonResponse({"message": "Пользователь успешно зарегистрирован и выполнен вход.",
                                         "user": get_user_data(user)}, status=201)

                except IntegrityError as e:
                    error_message = str(e).lower()
                    if 'unique constraint' in error_message:
                        if 'username' in error_message:
                            return JsonResponse({"error": "Пользователь с таким именем пользователя уже существует."},
                                                status=409)
                        elif 'email' in error_message:
                            return JsonResponse({"error": "Пользователь с таким email уже существует."}, status=409)
                    return JsonResponse({"error": f"Ошибка базы данных при регистрации: {str(e)}"}, status=500)
                except ValueError as e:
                    return JsonResponse({"error": str(e)}, status=400)
                except Exception as e:
                    return JsonResponse({"error": f"Произошла непредвиденная ошибка при регистрации: {str(e)}"},
                                        status=500)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Некорректный JSON формат запроса."}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Произошла непредвиденная ошибка: {str(e)}"}, status=500)

    return JsonResponse({"error": "Только метод POST разрешен для регистрации."}, status=405)


# Авторизация пользователя
@csrf_exempt
def user_login(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            username = body.get("username")
            password = body.get("password")

            if not all([username, password]):
                return JsonResponse({"error": "Необходимо указать имя пользователя и пароль."}, status=400)

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return JsonResponse({"message": "Вход успешно выполнен.", "user": get_user_data(user)}, status=200)
            else:
                return JsonResponse({"error": "Неверное имя пользователя или пароль."}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Некорректный JSON формат запроса."}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Произошла непредвиденная ошибка при входе: {str(e)}"}, status=500)

    return JsonResponse({"error": "Только метод POST разрешен для входа."}, status=405)


# Выход пользователя
@csrf_exempt
def user_logout(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            logout(request)
            return JsonResponse({"message": "Выход успешно выполнен."}, status=200)
        else:
            return JsonResponse({"error": "Пользователь не авторизован."}, status=401)
    return JsonResponse({"error": "Только метод POST разрешен для выхода."}, status=405)


# Получение информации о текущем авторизованном пользователе
def get_current_user_info(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return JsonResponse({"user": get_user_data(request.user)}, status=200)
        else:
            return JsonResponse({"error": "Пользователь не авторизован."}, status=401)
    return JsonResponse({"error": "Только метод GET разрешен для получения информации о текущем пользователе."},
                        status=405)


# Получение информации об авторизованном пользователе по ID
def get_user_by_id(request, user_id):
    if request.method == "GET":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Для доступа к информации о других пользователях необходимо авторизоваться."},
                                status=401)
        try:
            user = User.objects.get(id=user_id)
            return JsonResponse(get_user_data(user), status=200)
        except User.DoesNotExist:
            return JsonResponse({"error": "Пользователь не найден."}, status=404)
        except Exception as e:
            return JsonResponse({"error": f"Произошла ошибка при получении пользователя по ID: {str(e)}"}, status=500)

    return JsonResponse({"error": "Только метод GET разрешен для получения пользователя по ID."}, status=405)


# Изменение адреса у пользователя
# @csrf_exempt
# def update_user_address(request):
#     if request.method == "PATCH":
#         if not request.user.is_authenticated:
#             return JsonResponse({"error": "Необходимо авторизоваться для обновления адреса."}, status=401)
#
#         current_user = request.user
#         try:
#             body = json.loads(request.body)
#             new_address = body.get("address")
#             new_postal_code = body.get("postal_code")
#
#             if new_address is not None:
#                 current_user.address = new_address
#             if new_postal_code is not None:
#                 current_user.postal_code = new_postal_code
#
#             current_user.save()
#             return JsonResponse({"message": "Адрес пользователя успешно обновлен.", "user": get_user_data(current_user)}, status=200)
#
#         except json.JSONDecodeError:
#             return JsonResponse({"error": "Некорректный JSON формат запроса."}, status=400)
#         except Exception as e:
#             return JsonResponse({"error": f"Произошла ошибка при обновлении адреса: {str(e)}"}, status=500)
#     return JsonResponse({"error": "Только метод PATCH"}, status=405)

@csrf_exempt
def update_user(request):
    if request.method == 'PATCH':
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Для обновления данных необходимо авторизоваться."}, status=401)

        try:
            body = json.loads(request.body)
            user = request.user

            # Поля, которые можно обновлять
            updatable_fields = ['username', 'email', 'full_name', 'phone', 'postal_code', 'address']

            # Проверяем, что все передаваемые поля разрешены для обновления
            invalid_fields = [field for field in body.keys() if field not in updatable_fields]
            if invalid_fields:
                return JsonResponse(
                    {"error": f"Невозможно обновить следующие поля: {', '.join(invalid_fields)}"},
                    status=400
                )

            # Обновляем email с дополнительной проверкой
            if 'email' in body:
                new_email = body['email']
                if User.objects.exclude(id=user.id).filter(email=new_email).exists():
                    return JsonResponse({"error": "Пользователь с таким email уже существует."}, status=409)
                user.email = new_email

            # Обновляем остальные поля
            if 'full_name' in body:
                user.full_name = body['full_name']

            if 'phone' in body:
                user.phone = body['phone']

            if 'username' in body:
                user.username = body['username']
            if 'address' in body:
                user.address = body['address']
            if 'postal_code' in body:
                user.postal_code = body['postal_code']
            user.save()

            return JsonResponse({
                "message": "Данные пользователя успешно обновлены.",
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Некорректный JSON формат запроса."}, status=400)
        except IntegrityError as e:
            return JsonResponse({"error": f"Ошибка базы данных при обновлении: {str(e)}"}, status=500)
        except Exception as e:
            return JsonResponse({"error": f"Произошла непредвиденная ошибка: {str(e)}"}, status=500)

    return JsonResponse(
        {"error": "Только метод PATCH разрешены для обновления данных пользователя."},
        status=405
    )
