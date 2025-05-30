import json
from django.http import JsonResponse
from .models import Product, ProductImage
from brand.models import Brand
from category.models import category
from django.views.decorators.csrf import csrf_exempt

# Получение всех продуктов
def get_all_products(request):
    products = Product.objects.filter(is_deleted=True) # товар удален из каталога или нет
    data = []

    for product in products:
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
            "is_deleted": product.is_deleted
        })

    return JsonResponse(data, safe=False)

# Добавление нового товара
@csrf_exempt
def create_product(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)

            brand_id = body.get("brand_id")
            category_ids = body.get("category_ids", [])
            name = body.get("name")
            price = body.get("price")
            description = body.get("description")
            country = body.get("country")
            movement_type = body.get("movement_type")
            caliber = body.get("caliber")
            case_material = body.get("case_material")
            dial_type = body.get("dial_type")
            bracelet_material = body.get("bracelet_material")
            water_resistance = body.get("water_resistance")
            glass_type = body.get("glass_type")
            dimensions = body.get("dimensions")
            is_deleted = body.get("is_deleted", False)

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

            return JsonResponse({"message": "Продукт успешно создан", "product_id": product.id}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Только метод POST"}, status=405)

#Мягкое удаление товара, остается в бд, в каталоге нет
@csrf_exempt
def delete_product(request, product_id):
    if request.method == "POST":
        try:
            product = Product.objects.get(id=product_id)
            product.is_deleted = True
            product.save()
            return JsonResponse({"message": "Данный продукт удален из каталога"}, status=200)
        except Product.DoesNotExist:
            return JsonResponse({"error": "Продукт с таким id не найден"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Только метод POST"}, status=405)

