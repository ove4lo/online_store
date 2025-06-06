import json
from django.http import JsonResponse
from .models import Product, ProductImage
from brand.models import Brand
from category.models import category
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

# Получение товаров по поиску, можно не передавать ничего, выведет все товары
@csrf_exempt
def get_products(request):
    if request.method == "GET":
        try:
            search = request.GET.get("search", "").strip()
            products = Product.objects.select_related("brand_id").prefetch_related("images", "category_id")

            if search:
                products = products.filter(
                    Q(name__icontains=search) |
                    Q(brand_id__name__icontains=search) |
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

            data = []
            for product in products:
                images = product.images.all()
                image_data = [
                    {
                        "url": request.build_absolute_uri(image.image.url),
                        "is_main": image.is_main
                    }
                    for image in images if image.image
                ]

                data.append({
                    "id": product.id,
                    "brand_id": product.brand_id.id if product.brand_id else None,
                    "category_ids": list(product.category_id.values_list('id', flat=True)),
                    "name": product.name,
                    "price": float(product.price),
                    "description": product.description,
                    "country": product.country,
                    "movement_type": product.movement_type,
                    "caliber": product.caliber,
                    "case_material": product.case_material,
                    "dial_type": product.dial_type,
                    "bracelet_material": product.bracelet_material,
                    "water_resistance": product.water_resistance,
                    "glass_type": product.glass_type,
                    "dimensions": product.dimensions,
                    "is_deleted": product.is_deleted,
                    "images": image_data
                })

            return JsonResponse(data, safe=False)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Только метод GET"}, status=405)

# Получение одного товара по его id
@csrf_exempt
def get_product_by_id(request, product_id):
    if request.method == "GET":
        try:
            product = Product.objects.get(id=product_id, is_deleted=False)

            images = product.images.all()
            image_data = [
                {
                    "url": request.build_absolute_uri(image.image.url),
                    "is_main": image.is_main
                }
                for image in images if image.image
            ]

            data = {
                "id": product.id,
                "brand_id": product.brand_id.id if product.brand_id else None,
                "category_ids": list(product.category_id.values_list('id', flat=True)),
                "name": product.name,
                "price": float(product.price),
                "description": product.description,
                "country": product.country,
                "movement_type": product.movement_type,
                "caliber": product.caliber,
                "case_material": product.case_material,
                "dial_type": product.dial_type,
                "bracelet_material": product.bracelet_material,
                "water_resistance": product.water_resistance,
                "glass_type": product.glass_type,
                "dimensions": product.dimensions,
                "is_deleted": product.is_deleted,
                "images": image_data
            }

            return JsonResponse(data, safe=False)

        except Product.DoesNotExist:
            return JsonResponse({"error": "Продукт не найден"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Только метод GET"}, status=405)

# Добавление нового товара
@csrf_exempt
def create_product(request):
    if request.method == "POST":
        try:
            brand_id = request.POST.get("brand_id")
            name = request.POST.get("name")
            price = request.POST.get("price")
            category_ids = request.POST.getlist("category_ids")
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
            is_deleted = request.POST.get("is_deleted", "false").lower() == "true"

            if not all([brand_id, name, price]):
                return JsonResponse({"error": "Не заполнены обязательные поля"}, status=400)

            brand = Brand.objects.get(id=brand_id)
            product = Product.objects.create(
                brand_id=brand,
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
                is_deleted=is_deleted
            )

            for cat_id in category_ids:
                cat = category.objects.get(id=cat_id)
                product.category_id.add(cat)

            # Изображения
            images = request.FILES.getlist("images")
            for idx, image_file in enumerate(images):
                ProductImage.objects.create(
                    product=product,
                    image=image_file,
                    is_main=(idx == 0)  # первая картинка главная
                )

            return JsonResponse({"message": "Продукт успешно создан", "product_id": product.id}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Только метод POST"}, status=405)

# Мягкое удаление товара, остается в бд, в каталоге нет
@csrf_exempt
def soft_delete_product(request, product_id):
    if request.method == "DELETE":
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

# Жесткое удаление товара, удаляется из бд
@csrf_exempt
def hard_delete_product(request, product_id):
    if request.method == "DELETE":
        try:
            product = Product.objects.get(id=product_id)
            product.delete()
            return JsonResponse({"message": "Продукт полностью удален из базы данных"}, status=200)
        except Product.DoesNotExist:
            return JsonResponse({"error": "Продукт с таким id не найден"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Только метод DELETE"}, status=405)

# Редактирование товара
@csrf_exempt
def edit_product(request, product_id):
    if request.method == "PATCH":
        try:
            product = Product.objects.get(id=product_id)

            # Проверка типа данных
            if request.content_type == "application/json":
                body = json.loads(request.body)
            else:
                body = request.POST

            # Обновление полей
            if "brand_id" in body:
                brand = Brand.objects.get(id=body.get("brand_id"))
                product.brand_id = brand

            if "name" in body:
                product.name = body.get("name")
            if "price" in body:
                product.price = body.get("price")
            if "description" in body:
                product.description = body.get("description")
            if "country" in body:
                product.country = body.get("country")
            if "movement_type" in body:
                product.movement_type = body.get("movement_type")
            if "caliber" in body:
                product.caliber = body.get("caliber")
            if "case_material" in body:
                product.case_material = body.get("case_material")
            if "dial_type" in body:
                product.dial_type = body.get("dial_type")
            if "bracelet_material" in body:
                product.bracelet_material = body.get("bracelet_material")
            if "water_resistance" in body:
                product.water_resistance = body.get("water_resistance")
            if "glass_type" in body:
                product.glass_type = body.get("glass_type")
            if "dimensions" in body:
                product.dimensions = body.get("dimensions")
            if "is_deleted" in body:
                product.is_deleted = str(body.get("is_deleted")).lower() == "true"

            # Обновление категорий
            category_ids = body.get("category_ids")
            if category_ids:
                if isinstance(category_ids, str):
                    category_ids = json.loads(category_ids)
                product.category_id.clear()
                for cat_id in category_ids:
                    cat = category.objects.get(id=cat_id)
                    product.category_id.add(cat)

            product.save()

            # Обновление изображений
            if request.FILES:
                product.images.all().delete()
                images = request.FILES.getlist("images")
                for idx, image_file in enumerate(images):
                    ProductImage.objects.create(
                        product=product,
                        image=image_file,
                        is_main=(idx == 0)
                    )

            return JsonResponse({"message": "Продукт обновлён успешно"}, status=200)

        except Product.DoesNotExist:
            return JsonResponse({"error": "Продукт не найден"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Только метод PATCH"}, status=405)