# Серверная часть проекта "Онлайн магазин часов"
Написано на **Python** и **Django** с **SQLite3**
## API для взаимодействия с пользователем:
### *По умолчанию взаимодейсвует с http://127.0.0.1:8000/api/*
1. #### Получение всех продуктов: ``` products/?search=<переменная> ```
+ получение всех товаров(ничего передавать не надо) 
``` products/ ```
+ поиск продукта по всем полям(регистрозависимый от кириллицы), кроме описания (название; категория цена, страна, тип механизма, калибр, корпус, циферблат, браслет, водозащита, стекло, габаритные размеры) 
``` 'products/?search=<переменная>' ```

Пример полученного результата:
```json
   [
    { 
        "id": 6,
        "brand_id": 1,
        "category_ids": [
            1,
            2
        ],
        "name": "Новые часы",
        "price": 15999.0,
        "description": "Обновлённое описание",
        "country": "Швейцария",
        "movement_type": null,
        "caliber": null,
        "case_material": null,
        "dial_type": null,
        "bracelet_material": null,
        "water_resistance": null,
        "glass_type": null,
        "dimensions": null,
        "is_deleted": false,
        "images": [
            {
                "url": "http://127.0.0.1:8000/media/product_images/SRPL11__1_kFbxt1R.jpg",
                "is_main": true
            },
            {
                "url": "http://127.0.0.1:8000/media/product_images/SRPL11_3dPqNTr.jpg",
                "is_main": false
            }
        ]
    }
]
```

2. #### Получение продукта по id ``` products/<int:product_id>/ ```
Пример идентичен из пункта 1.

3. #### Создание заказа ``` orders/create/ ```
Пример отправления данных в формате JSON:
``` json
{
  "user_id": 1,
  "address": "г. Владивосток, ул. Калинина, д. 8",
  "postal_code": "690000",
  "items": [
    { "product_id": 1, "quantity": 1 },
    { "product_id": 2, "quantity": 2 }
  ]
}
```

4. #### Получение заказа по его id ``` orders/<int:order_id>/ ```
Пример полученного результата:
``` json
  {
    "user": {
        "full_name": "Test Test",
        "phone": "79241263771",
        "email": "test",
        "address": "г. Владивосток, ул. Калинина, д. 8"
    },
    "items": [
        {
            "name": "FFFFFFFFFFFF",
            "quantity": 1,
            "price": 4444.0
        },
        {
            "name": "try",
            "quantity": 2,
            "price": 4000.0
        }
    ],
    "total_price": 12444.0,
    "created_at": "2025-06-01 06:29:06",
    "status": "Доставлен"
}
```

5. #### Получение всех заказов пользователя по его id ``` orders/user/<int:user_id>/ ```
Пример полученного результата:
``` json
[
    {
        "order_id": 1,
        "created_at": "2025-06-01 06:29:06",
        "user": "Test Test",
        "total_price": 12444.0,
        "status": "Доставлен"
    }
]
```
