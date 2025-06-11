# product/views.py
import json
from django.http import JsonResponse
from .models import Product, ProductImage
from brand.models import Brand
from category.models import category
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.db import transaction

User = get_user_model()


# Формирования данных продукта
def get_product_data(product_obj, request):

    images_data = [
        {
            "url": request.build_absolute_uri(image.image.url),
            "is_main": image.is_main
        }
        for image in product_obj.images.all() if image.image
    ]

    return {
        "id": product_obj.id,
        "brand_id": product_obj.brand.id if product_obj.brand else None,
        "brand_name": product_obj.brand.name if product_obj.brand else None,
        "category_ids": list(product_obj.category.values_list('id', flat=True)),
        "category_names": list(product_obj.category.values_list('name', flat=True)),
        "name": product_obj.name,
        "price": float(product_obj.price),
        "description": product_obj.description,
        "country": product_obj.country,
        "movement_type": product_obj.movement_type,
        "caliber": product_obj.caliber,
        "case_material": product_obj.case_material,
        "dial_type": product_obj.dial_type,
        "bracelet_material": product_obj.bracelet_material,
        "water_resistance": product_obj.water_resistance,
        "glass_type": product_obj.glass_type,
        "dimensions": product_obj.dimensions,
        "is_deleted": product_obj.is_deleted,
        "images": images_data
    }

# Получение товаров по поиску, фильтрации и сортировке
@csrf_exempt
def get_products(request):
    if request.method == "GET":
        try:
            search = request.GET.get("search", "").strip()
            products = Product.objects.select_related("brand").prefetch_related("images", "category")

            if search:
                products = products.filter(
                    Q(name__icontains=search) |
                    Q(brand__name__icontains=search) |
                    Q(country__icontains=search) |
                    Q(movement_type__icontains=search) |
                    Q(caliber__icontains=search) |
                    Q(case_material__icontains=search) |
                    Q(dial_type__icontains=search) |
                    Q(bracelet_material__icontains=search) |
                    Q(water_resistance__icontains=search) |
                    Q(glass_type__icontains=search) |
                    Q(dimensions__icontains=search)
                )

            country = request.GET.get("country")
            movement_type = request.GET.get("movement_type")
            case_material = request.GET.get("case_material")
            glass_type = request.GET.get("glass_type")

            filters = {}

            if country: filters["country"] = country
            if movement_type: filters["movement_type"] = movement_type
            if case_material: filters["case_material"] = case_material
            if glass_type: filters["glass_type"] = glass_type

            if filters:
                products = products.filter(**filters)

            price_sort = request.GET.get('price_sort', 'asc')
            name_sort = request.GET.get('name_sort', 'asc')

            order_by = []
            order_by.append('price' if price_sort == 'asc' else '-price')
            order_by.append('name' if name_sort == 'asc' else '-name')

            products = products.order_by(*order_by)

            data = [get_product_data(product, request) for product in products]

            return JsonResponse(data, safe=False)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Только метод GET"}, status=405)


# Получение одного товара по его id
@csrf_exempt
def get_product_by_id(request, product_id):
    if request.method == "GET":
        try:
            product = Product.objects.select_related("brand").prefetch_related("images", "category").get(id=product_id,
                                                                                                         is_deleted=False)

            data = get_product_data(product, request)

            return JsonResponse(data, safe=False)

        except Product.DoesNotExist:
            return JsonResponse({"error": "Продукт не найден"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Только метод GET"}, status=405)


# Добавление нового товара (только для админа)
@csrf_exempt
def create_product(request):
    if request.method == "POST":
        # Проверка авторизации и прав администратора
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Для создания продукта необходимо авторизоваться."}, status=401)
        if not request.user.is_staff:
            return JsonResponse({"error": "У вас нет прав для создания продукта."}, status=403)

        try:

            brand_id_str = request.POST.get("brand_id")
            name = request.POST.get("name")
            price_str = request.POST.get("price")
            category_ids_str_list = request.POST.getlist("category_ids")
            description = request.POST.get("description")
            country = request.POST.get("country")
            movement_type = request.POST.get("movement_type")
            caliber = request.POST.get("caliber")
            case_material = request.POST.get("case_material")
            dial_type = request.POST.get("dial_type")
            bracelet_material = request.POST.get("bracelet_material")
            water_resistance = request.POST.get("water_resistance")
            glass_type = request.POST.get("glass_type")
            dimensions = request.POST.get("dimensions")

            if not all([brand_id_str, name, price_str]):
                return JsonResponse({"error": "Не заполнены обязательные поля: brand_id, name, price"}, status=400)

            # Валидация и конвертация ID и цены
            try:
                brand_id = int(brand_id_str)
            except (ValueError, TypeError):
                return JsonResponse({"error": "brand_id должен быть целым числом."}, status=400)

            try:
                price = Decimal(price_str)
                if price <= 0:
                    return JsonResponse({"error": "Цена должна быть положительным числом."}, status=400)
            except (ValueError, TypeError):
                return JsonResponse({"error": "Цена должна быть числом."}, status=400)

            category_ids = []
            for cat_id_str in category_ids_str_list:
                try:
                    category_ids.append(int(cat_id_str))
                except (ValueError, TypeError):
                    return JsonResponse({"error": f"category_id '{cat_id_str}' должен быть целым числом."}, status=400)

            with transaction.atomic():
                try:
                    brand = Brand.objects.get(id=brand_id)
                except Brand.DoesNotExist:
                    return JsonResponse({"error": "Бренд с указанным ID не найден."}, status=404)

                product = Product.objects.create(
                    brand=brand,
                    name=name,
                    price=price,
                    description=description,
                    country=country,
                    movement_type=movement_type,
                    caliber=caliber,
                    case_material=case_material,
                    dial_type=dial_type,
                    bracelet_material=bracelet_material,
                    water_resistance=water_resistance,
                    glass_type=glass_type,
                    dimensions=dimensions,
                    is_deleted=False
                )

                # Категории
                for cat_id in category_ids:
                    try:
                        cat = category.objects.get(id=cat_id)
                        product.category.add(cat)
                    except category.DoesNotExist:
                        raise ValueError(f"Категория с ID {cat_id} не найдена. Создание продукта отменено.")

                # Обработка изображений
                images_files = request.FILES.getlist("images")
                if not images_files:
                    return JsonResponse({"error": "Необходимо загрузить хотя бы одно изображение для продукта."},
                                        status=400)

                for idx, image_file in enumerate(images_files):
                    ProductImage.objects.create(
                        product=product,
                        image=image_file,
                        is_main=(idx == 0)
                    )

            return JsonResponse({"message": "Продукт успешно создан", "product_id": product.id}, status=201)

        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Произошла ошибка при создании продукта: {str(e)}"}, status=500)

    return JsonResponse({"error": "Только метод POST"}, status=405)


# Мягкое удаление товара (только для админа)
@csrf_exempt
def soft_delete_product(request, product_id):
    if request.method == "DELETE":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Необходимо авторизоваться."}, status=401)
        if not request.user.is_staff:
            return JsonResponse({"error": "У вас нет прав для удаления продукта."}, status=403)

        try:
            product = Product.objects.get(id=product_id)
            product.is_deleted = True
            product.save()
            return JsonResponse({"message": "Данный продукт удален из каталога"}, status=200)
        except Product.DoesNotExist:
            return JsonResponse({"error": "Продукт с таким id не найден"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Только метод DELETE"}, status=405)


# Жесткое удаление товара (только для админа)
@csrf_exempt
def hard_delete_product(request, product_id):
    if request.method == "DELETE":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Необходимо авторизоваться."}, status=401)
        if not request.user.is_staff:
            return JsonResponse({"error": "У вас нет прав для удаления продукта."}, status=403)

        try:
            product = Product.objects.get(id=product_id)
            product.delete()
            return JsonResponse({"message": "Продукт полностью удален из базы данных"}, status=200)
        except Product.DoesNotExist:
            return JsonResponse({"error": "Продукт с таким id не найден"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Только метод DELETE"}, status=405)


# Редактирование товара (Только для админа)
@csrf_exempt
def edit_product(request, product_id):
    if request.method == "PATCH":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Необходимо авторизоваться."}, status=401)
        if not request.user.is_staff:
            return JsonResponse({"error": "У вас нет прав для редактирования продукта."}, status=403)

        try:
            product = Product.objects.get(id=product_id)

            if request.content_type == "application/json":
                body = json.loads(request.body)
                category_ids_from_body = body.get("category_ids")
            else:
                body = request.POST
                category_ids_from_body = request.POST.getlist("category_ids")

            with transaction.atomic():
                # Обновление полей
                if "brand_id" in body:
                    brand_id_str = body.get("brand_id")
                    try:
                        brand_id = int(brand_id_str)
                    except (ValueError, TypeError):
                        raise ValueError("brand_id должен быть целым числом.")

                    try:
                        brand = Brand.objects.get(id=brand_id)
                        product.brand = brand
                    except Brand.DoesNotExist:
                        raise ValueError("Бренд с указанным ID не найден.")

                if "name" in body:
                    product.name = body.get("name")
                if "price" in body:
                    price_str = body.get("price")
                    try:
                        price = Decimal(price_str)
                        if price <= 0:
                            raise ValueError("Цена должна быть положительным числом.")
                        product.price = price  # DecimalField
                    except (ValueError, TypeError):
                        raise ValueError("Некорректное значение цены.")

                if "description" in body: product.description = body.get("description")
                if "country" in body: product.country = body.get("country")
                if "movement_type" in body: product.movement_type = body.get("movement_type")
                if "caliber" in body: product.caliber = body.get("caliber")
                if "case_material" in body: product.case_material = body.get("case_material")
                if "dial_type" in body: product.dial_type = body.get("dial_type")
                if "bracelet_material" in body: product.bracelet_material = body.get("bracelet_material")
                if "water_resistance" in body: product.water_resistance = body.get("water_resistance")
                if "glass_type" in body: product.glass_type = body.get("glass_type")
                if "dimensions" in body: product.dimensions = body.get("dimensions")
                if "is_deleted" in body:
                    product.is_deleted = str(body.get("is_deleted")).lower() == "true"

                # Обновление категорий
                if category_ids_from_body is not None:
                    parsed_category_ids = []
                    if isinstance(category_ids_from_body, str):
                        try:
                            if category_ids_from_body.strip().startswith('['):
                                category_ids_from_body = json.loads(category_ids_from_body)
                            else:
                                category_ids_from_body = [int(x.strip()) for x in category_ids_from_body.split(',') if
                                                          x.strip()]
                        except Exception:
                            raise ValueError("category_ids должен быть списком ID или строкой JSON-массива.")

                    if not isinstance(category_ids_from_body, list):
                        raise ValueError("category_ids должен быть списком ID.")

                    for cat_id_val in category_ids_from_body:
                        try:
                            parsed_category_ids.append(int(cat_id_val))
                        except (ValueError, TypeError):
                            raise ValueError(f"category_id '{cat_id_val}' должен быть целым числом.")

                    # Очищаем старые и добавляем новые
                    product.category.clear()
                    for cat_id in parsed_category_ids:
                        try:
                            cat = category.objects.get(id=cat_id)
                            product.category.add(cat)  # Изменено: product.category_id -> product.category
                        except category.DoesNotExist:
                            raise ValueError(f"Категория с ID {cat_id} не найдена.")

                product.save()

                if request.FILES:
                    product.images.all().delete()
                    images = request.FILES.getlist("images")
                    if not images:
                        raise ValueError("При обновлении изображений не было передано ни одного файла.")
                    for idx, image_file in enumerate(images):
                        ProductImage.objects.create(
                            product=product,
                            image=image_file,
                            is_main=(idx == 0)
                        )

            return JsonResponse({"message": "Продукт обновлён успешно", "product_id": product.id}, status=200)

        except Product.DoesNotExist:
            return JsonResponse({"error": "Продукт не найден"}, status=404)
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Произошла ошибка при редактировании продукта: {str(e)}"}, status=500)

    return JsonResponse({"error": "Только метод PATCH"}, status=405)
