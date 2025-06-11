import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import category
from django.contrib.auth import get_user_model

User = get_user_model()

# Получение всех категорий
@csrf_exempt
def get_categories(request):
    if request.method == "GET":
        try:
            categories = category.objects.all().order_by('name')
            data = [
                {
                    "id": cat.id,
                    "name": cat.name,
                    "description": cat.description if cat.description else ""
                }
                for cat in categories
            ]
            return JsonResponse(data, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Только метод GET"}, status=405)


# Создание новой категории (только для админа)
@csrf_exempt
def create_category(request):
    if request.method == "POST":
        # Проверка авторизации и прав администратора
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Для создания категории необходимо авторизоваться."}, status=401)
        if not request.user.is_staff:
            return JsonResponse({"error": "У вас нет прав для создания категории."}, status=403)

        try:
            body = json.loads(request.body)
            name = body.get("name")
            description = body.get("description", "")

            if not name:
                return JsonResponse({"error": "Название категории обязательно."}, status=400)

            if category.objects.filter(name__iexact=name).exists():  # Проверка на уникальность
                return JsonResponse({"error": "Категория с таким названием уже существует."}, status=409)

            new_category = category.objects.create(name=name, description=description)
            return JsonResponse(
                {"message": "Категория успешно создана.", "id": new_category.id, "name": new_category.name}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Некорректный JSON формат запроса."}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Произошла ошибка при создании категории: {str(e)}"}, status=500)
    return JsonResponse({"error": "Только метод POST"}, status=405)

# Редактирование категории (только для админа)
@csrf_exempt
def update_category(request, category_id):
    if request.method == "PATCH":
        # Проверка авторизации и прав администратора
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Для редактирования категории необходимо авторизоваться."}, status=401)
        if not request.user.is_staff:
            return JsonResponse({"error": "У вас нет прав для редактирования категории."}, status=403)

        try:
            cat_obj = category.objects.get(id=category_id)
            body = json.loads(request.body)

            name = body.get("name")
            description = body.get("description")

            if name:
                if category.objects.filter(name__iexact=name).exclude(id=category_id).exists():
                    return JsonResponse({"error": "Категория с таким названием уже существует."}, status=409)
                cat_obj.name = name

            if description is not None:
                cat_obj.description = description

            cat_obj.save()
            return JsonResponse({"message": "Категория успешно обновлена.", "id": cat_obj.id, "name": cat_obj.name},
                                status=200)

        except category.DoesNotExist:
            return JsonResponse({"error": "Категория не найдена."}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Некорректный JSON формат запроса."}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Произошла ошибка при обновлении категории: {str(e)}"}, status=500)
    return JsonResponse({"error": "Только метод PATCH"}, status=405)


# Удаление категории (только для менеджера)
@csrf_exempt
def delete_category(request, category_id):
    if request.method == "DELETE":
        # Проверка авторизации и прав администратора
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Для удаления категории необходимо авторизоваться."}, status=401)
        if not request.user.is_staff:
            return JsonResponse({"error": "У вас нет прав для удаления категории."}, status=403)

        try:
            cat_obj = category.objects.get(id=category_id)
            cat_obj.delete()
            return JsonResponse({"message": "Категория успешно удалена."}, status=200)
        except category.DoesNotExist:
            return JsonResponse({"error": "Категория не найдена."}, status=404)
        except Exception as e:
            return JsonResponse({"error": f"Произошла ошибка при удалении категории: {str(e)}"}, status=500)
    return JsonResponse({"error": "Только метод DELETE"}, status=405)
