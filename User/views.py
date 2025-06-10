from User.models import User
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

# Добавление нового пользователя
@csrf_exempt
def create_user(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)

            username = body.get("username")
            email = body.get("email")
            password = body.get("password")
            full_name = body.get("full_name")
            phone = body.get("phone")
            is_staff = body.get("is_staff", False)
            is_active = body.get("is_active", True)

            if not all([username, email, password, full_name, phone]):
                return JsonResponse({"error": "Не заполнены обязательные поля"}, status=400)

            # Проверка, существует ли уже пользователь с таким логином
            if User.objects.filter(username=username).exists():
                return JsonResponse({"error": "Пользователь с таким username уже существует"}, status=400)

            # Создание пользователя
            user = User(
                username=username,
                email=email,
                full_name=full_name,
                phone=phone,
                is_staff=is_staff,
                is_active=is_active
            )
            user.password = password
            user.save()

            return JsonResponse({"message": "Пользователь успешно создан", "user_id": user.id}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Только метод POST"}, status=405)

# получения пользователя по id
def get_user_by_id(request, user_id):
    if request.method == "GET":
        try:
            # Получаем пользователя по id или возвращаем 404 если не найден
            user = User.objects.get(id=user_id)

            # Формируем ответ с данными пользователя
            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "phone": user.phone,
                "is_staff": user.is_staff,
                "is_active": user.is_active,
            }

            return JsonResponse(user_data, status=200)

        except User.DoesNotExist:
            return JsonResponse({"error": "Пользователь не найден"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Только метод GET"}, status=405)
