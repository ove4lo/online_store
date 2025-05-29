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
