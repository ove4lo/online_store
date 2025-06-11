import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db import transaction

User = get_user_model()

# Формирование данных пользователя в JSON-ответе
def get_user_data(user):

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "phone": user.phone,
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
                        phone=phone
                    )

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
    return JsonResponse({"error": "Только метод GET разрешен для получения информации о текущем пользователе."}, status=405)

# Получение информации об авторизованном пользователе по ID
def get_user_by_id(request, user_id):
    if request.method == "GET":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Для доступа к информации о других пользователях необходимо авторизоваться."}, status=401)
        try:
            user = User.objects.get(id=user_id)
            return JsonResponse(get_user_data(user), status=200)
        except User.DoesNotExist:
            return JsonResponse({"error": "Пользователь не найден."}, status=404)
        except Exception as e:
            return JsonResponse({"error": f"Произошла ошибка при получении пользователя по ID: {str(e)}"}, status=500)

    return JsonResponse({"error": "Только метод GET разрешен для получения пользователя по ID."}, status=405)