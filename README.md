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

6.  #### Регистрация пользователя POST ``` /user/register/ ```
``` json
{
    "username": "test",
    "email": "test@example.com",
    "password": "SecurePassword123!",
    "full_name": "Новый Клиент",
    "phone": "1112223333",
    "address": "Улица Заказов, д. 15, кв. 20", 
    "postal_code": "456789"                  
}
```
Пример полученного результата:
``` json
{
    "message": "Пользователь успешно зарегистрирован и выполнен вход.",
    "user": {
        "id": 2,
        "username": "test",
        "email": "test@example.com",
        "full_name": "Новый Клиент",
        "phone": "1112223333",
        "address": "Улица Заказов, д. 15, кв. 20",
        "postal_code": "456789",
        "is_staff": false,
        "is_active": true,
        "created_at": "2025-06-12T03:01:23.938851+00:00",
        "updated_at": "2025-06-12T03:01:23.938885+00:00"
    }
}
```
В куках передается sessionId
7.  #### Авторизация пользователя POST ```/user/login/ ```
``` json
{
    "username": "admin",
    "password": "admin"
}
```
Пример полученного результата:
``` json
{
    "message": "Вход успешно выполнен.",
    "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@gmail.com",
        "full_name": "admin",
        "phone": "70000000000",
        "is_staff": true,
        "is_active": true,
        "created_at": "2025-06-11T05:58:21.687118+00:00",
        "updated_at": "2025-06-11T05:58:21.687118+00:00"
    }
}
```
При неверном логине или пароле - 401:
```json
{
    "error": "Неверное имя пользователя или пароль."
}
```
В куках передается sessionId
8.  #### Выход пользователя POST ``` /user/logout/ ```
Пример полученного результата:
``` json
{
    "message": "Выход успешно выполнен."
}
```
Из куки удаляется sessionId
Если пользователь не авторизован, то ответ от сервера 401:
``` json
{
    "error": "Пользователь не авторизован."
}
```
9.  #### Получение информации о текущем пользователе GET ``` /user/current/ ```
Фронт автоматически прикрепляет sessionId к запросу, поэтому достаточно отправить просто запрос GET
Пример полученного результата:
``` json
{
    "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@gmail.com",
        "full_name": "admin",
        "phone": "70000000000",
        "is_staff": true,
        "is_active": true,
        "created_at": "2025-06-11T05:58:21.687118+00:00",
        "updated_at": "2025-06-11T05:58:21.687118+00:00"
    }
}
```
Если пользователь не авторизован, то ответ от сервера 401:
``` json
{
    "error": "Пользователь не авторизован."
}
```
10.  #### Получение информации об пользователе по его id GET ``` /user/<int:user_id>/ ```
Пример полученного результата:
``` json
{
    "id": 3,
    "username": "test",
    "email": "test@example.com",
    "full_name": "Test",
    "phone": "89241263771",
    "is_staff": false,
    "is_active": true,
    "created_at": "2025-06-11T06:13:43.294011+00:00",
    "updated_at": "2025-06-11T06:13:43.294011+00:00"
}
```
11.  #### Изменение у пользователя адрес доставки PATCH ``` user/address/ ```
``` json
{
    "address": "Тестовый адрес пользователя",
    "postal_code": "12345"
}
```
Пример полученного результата:
``` json
{
    "message": "Адрес пользователя успешно обновлен.",
    "user": {
        "id": 2,
        "username": "test",
        "email": "test@example.com",
        "full_name": "Новый Клиент",
        "phone": "1112223333",
        "address": "Тестовый адрес пользователя",
        "postal_code": "12345",
        "is_staff": false,
        "is_active": true,
        "created_at": "2025-06-12T03:01:23.938851+00:00",
        "updated_at": "2025-06-12T03:18:41.481137+00:00"
    }
}
```
12.  #### Создание заказа у текущего пользователя POST ``` orders/create/ ```
``` json
{
    "items": [
        {
            "product_id": 1,
            "quantity": 1
        },
        {
            "product_id": 2,
            "quantity": 3
        }
    ]
}
```
Пример полученного результата:
``` json
{
    "message": "Заказ успешно создан",
    "order_id": 1
}
```
