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
from django.core.files.storage import default_storage
import uuid
import os

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
            product = Product.objects.select_related("brand").prefetch_related("images", "category").get(id=product_id)

            # Проверка прав администратора для скрытых продуктов
            if product.is_deleted and not request.user.is_staff:
                return JsonResponse({"error": "Продукт скрыт"}, status=403)

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
    if request.method != "POST":
        return JsonResponse({"error": "Разрешены только POST-запросы"}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Необходимо авторизоваться"}, status=401)
    if not request.user.is_staff:
        return JsonResponse({"error": "Требуются права администратора"}, status=403)

    try:
        required_fields = {
            'brand_id': request.POST.get("brand_id"),
            'name': request.POST.get("name"),
            'price': request.POST.get("price")
        }

        if not all(required_fields.values()):
            missing = [k for k, v in required_fields.items() if not v]
            return JsonResponse(
                {"error": f"Не заполнены обязательные поля: {', '.join(missing)}"},
                status=400
            )

        try:
            brand_id = int(required_fields['brand_id'])
            price = Decimal(required_fields['price'])
            if price <= 0:
                return JsonResponse({"error": "Цена должна быть положительной"}, status=400)
        except (ValueError, TypeError):
            return JsonResponse({"error": "Некорректный формат числовых полей"}, status=400)

        category_ids = []
        for cat_id in request.POST.getlist("category_ids", []):
            try:
                category_ids.append(int(cat_id))
            except ValueError:
                return JsonResponse({"error": f"Некорректный ID категории: {cat_id}"}, status=400)

        # Дополнительные поля
        optional_fields = {
            'description': request.POST.get("description", ""),
            'country': request.POST.get("country", ""),
            'movement_type': request.POST.get("movement_type", ""),
            'caliber': request.POST.get("caliber", ""),
            'case_material': request.POST.get("case_material", ""),
            'dial_type': request.POST.get("dial_type", ""),
            'bracelet_material': request.POST.get("bracelet_material", ""),
            'water_resistance': request.POST.get("water_resistance", ""),
            'glass_type': request.POST.get("glass_type", ""),
            'dimensions': request.POST.get("dimensions", "")
        }

        with transaction.atomic():
            try:
                brand = Brand.objects.get(id=brand_id)
            except Brand.DoesNotExist:
                return JsonResponse({"error": "Указанный бренд не существует"}, status=400)

            product = Product.objects.create(
                brand=brand,
                name=required_fields['name'],
                price=price,
                **optional_fields,
                is_deleted=False
            )

            for cat_id in category_ids:
                try:
                    cat = category.objects.get(id=cat_id)
                    product.category.add(cat)
                except category.DoesNotExist:
                    transaction.set_rollback(True)
                    return JsonResponse({"error": f"Категория {cat_id} не найдена"}, status=400)

            images = request.FILES.getlist("images")
            if not images:
                transaction.set_rollback(True)
                return JsonResponse({"error": "Необходимо загрузить минимум 1 изображение"}, status=400)

            saved_images = []
            for idx, img in enumerate(images):
                ext = os.path.splitext(img.name)[1].lower()
                if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
                    transaction.set_rollback(True)
                    return JsonResponse({"error": "Допустимы только JPG/PNG/WEBP изображения"}, status=400)

                filename = f"product_images/{uuid.uuid4()}{ext}"
                file_path = default_storage.save(filename, img)

                saved_images.append(
                    ProductImage.objects.create(
                        product=product,
                        image=file_path,
                        is_main=(idx == 0)
                    )
                )

        image_urls = [img.image.url for img in saved_images]

        return JsonResponse({
            "success": True,
            "product_id": product.id,
            "name": product.name,
            "price": str(product.price),
            "categories": list(product.category.values_list('id', flat=True)),
            "images": image_urls
        }, status=201)

    except Exception as e:
        return JsonResponse({"error": f"Ошибка сервера: {str(e)}"}, status=500)

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
    if request.method != "POST":
        return JsonResponse({"error": "Разрешены только POST-запросы"}, status=405)

    # Проверка авторизации и прав
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Необходимо авторизоваться"}, status=401)
    if not request.user.is_staff:
        return JsonResponse({"error": "Требуются права администратора"}, status=403)

    try:
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({"error": "Продукт не найден"}, status=404)

        with transaction.atomic():
            if 'brand_id' in request.POST:
                try:
                    brand = Brand.objects.get(id=int(request.POST['brand_id']))
                    product.brand = brand
                except (ValueError, Brand.DoesNotExist):
                    return JsonResponse({"error": "Указанный бренд не существует"}, status=400)

            if 'name' in request.POST:
                product.name = request.POST['name']

            if 'price' in request.POST:
                try:
                    price = Decimal(request.POST['price'])
                    if price <= 0:
                        return JsonResponse({"error": "Цена должна быть положительной"}, status=400)
                    product.price = price
                except (ValueError, TypeError):
                    return JsonResponse({"error": "Некорректный формат цены"}, status=400)

            optional_fields = [
                'description', 'country', 'movement_type', 'caliber',
                'case_material', 'dial_type', 'bracelet_material',
                'water_resistance', 'glass_type', 'dimensions'
            ]

            for field in optional_fields:
                if field in request.POST:
                    setattr(product, field, request.POST[field])

            product.save()

            if 'category_ids' in request.POST:
                product.category.clear()
                for cat_id in request.POST.getlist('category_ids'):
                    try:
                        cat = category.objects.get(id=int(cat_id))
                        product.category.add(cat)
                    except (ValueError, category.DoesNotExist):
                        transaction.set_rollback(True)
                        return JsonResponse({"error": f"Категория {cat_id} не найдена"}, status=400)

            if 'images' in request.FILES:
                if 'clear_old_images' in request.POST and request.POST['clear_old_images'].lower() == 'true':
                    for img in product.images.all():
                        img.delete()

                images = request.FILES.getlist('images')
                for idx, img in enumerate(images):
                    ext = os.path.splitext(img.name)[1].lower()
                    if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
                        transaction.set_rollback(True)
                        return JsonResponse({"error": "Допустимы только JPG/PNG/WEBP изображения"}, status=400)

                    filename = f"product_images/{uuid.uuid4()}{ext}"
                    file_path = default_storage.save(filename, img)

                    is_main = (idx == 0) and not product.images.filter(is_main=True).exists()

                    ProductImage.objects.create(
                        product=product,
                        image=file_path,
                        is_main=is_main
                    )

            if 'main_image_id' in request.POST:
                try:
                    new_main_id = int(request.POST['main_image_id'])
                    new_main = ProductImage.objects.get(id=new_main_id, product=product)

                    ProductImage.objects.filter(product=product).update(is_main=False)
                    new_main.is_main = True
                    new_main.save()
                except (ValueError, ProductImage.DoesNotExist):
                    return JsonResponse({"error": "Некорректный ID изображения"}, status=400)

        product.refresh_from_db()
        return JsonResponse({
            "success": True,
            "product": {
                "id": product.id,
                "name": product.name,
                "price": str(product.price),
                "brand": product.brand.name,
                "categories": list(product.category.values_list('id', flat=True)),
                "images": [
                    {
                        "id": img.id,
                        "url": img.image.url,
                        "is_main": img.is_main
                    } for img in product.images.all()
                ]
            }
        })

    except Exception as e:
        return JsonResponse({"error": f"Ошибка сервера: {str(e)}"}, status=500)


@csrf_exempt
def get_all_parameters(request):
    if request.method == "GET":
        try:
            countries = Product.objects.exclude(country__isnull=True).exclude(country__exact='').order_by('country').values_list('country', flat=True).distinct()
            movement_types = Product.objects.exclude(movement_type__isnull=True).exclude(movement_type__exact='').order_by('movement_type').values_list('movement_type', flat=True).distinct()
            case_materials = Product.objects.exclude(case_material__isnull=True).exclude(case_material__exact='').order_by('case_material').values_list('case_material', flat=True).distinct()
            glass_types = Product.objects.exclude(glass_type__isnull=True).exclude(glass_type__exact='').order_by('glass_type').values_list('glass_type', flat=True).distinct()
            data = {
                "countries": list(countries),
                "movement_types": list(movement_types),
                "case_materials": list(case_materials),
                "glass_types": list(glass_types),
            }

            return JsonResponse(data, safe=False)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Только метод GET"}, status=405)

@csrf_exempt
def update_product_status(request, product_id):
    if request.method == "PATCH":
        try:
            # Проверка авторизации и прав
            if not request.user.is_authenticated:
                return JsonResponse({"error": "Необходимо авторизоваться"}, status=401)
            if not request.user.is_staff:
                return JsonResponse({"error": "Недостаточно прав"}, status=403)

            product = Product.objects.get(id=product_id)
            data = json.loads(request.body)
            product.is_deleted = data['is_deleted']
            product.save()

            return JsonResponse({"success": True}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Только метод PATCH"}, status=405)