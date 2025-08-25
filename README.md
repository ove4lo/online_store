# ONLINE_STORE

*Онлайн-магазин часов с пользовательским интерфейсом и кастомной админ-панелью*

![last-commit](https://img.shields.io/github/last-commit/ove4lo/dds-test-task?style=flat&logo=git&logoColor=white&color=0080ff)
![repo-top-language](https://img.shields.io/github/languages/top/ove4lo/dds-test-task?style=flat&color=0080ff)
![repo-language-count](https://img.shields.io/github/languages/count/ove4lo/dds-test-task?style=flat&color=0080ff)

*Создано с использованием следующих технологий:*

![Markdown](https://img.shields.io/badge/Markdown-000000.svg?style=flat&logo=Markdown&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED.svg?style=flat&logo=Docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB.svg?style=flat&logo=Python&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20.svg?style=flat&logo=Django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1.svg?style=flat&logo=PostgreSQL&logoColor=white)

---

## Содержание

- [Обзор](#overview)
- [Возможности](#features)
- [Начало работы](#getting-started)
  - [Предварительные требования](#prerequisites)
  - [Установка](#installation)
  - [Использование](#usage)
- [API Эндпоинты](#api-endpoints)

---

## Обзор <a name="overview"></a>

ONLINE_STORE — это веб-сервис, реализованный на Django и SQLite, предназначенный для продажи часов.  
Проект поддерживает все базовые функции интернет-магазина: регистрация пользователей, просмотр каталога, корзина, заказы и избранное. Для администраторов реализована **кастомная админ-панель** с расширенным управлением товарами, заказами и пользователями.  

фронтенд для онлайн-магазина: https://github.com/v1veX/online-store

фронтенд для админ-панели: https://github.com/ove4lo/admin-panel

---

## Возможности  <a name="features"></a>

- 🛍️ **Каталог товаров**: просмотр, фильтрация и поиск часов.  
- 📦 **Заказы**: создание заказов, просмотр своих заказов пользователями, управление статусами заказов администраторами.  
- ❤️ **Избранное**: добавление товаров в список желаемого, удаление и очистка.  
- 🛒 **Корзина**: добавление, удаление и редактирование товаров в корзине.  
- 👤 **Пользователи**: регистрация, авторизация, профиль, обновление данных.  
- 🛠️ **Кастомная админ-панель**: управление товарами, брендами, категориями и заказами.  

---

## Начало работы   <a name="getting-started"></a>

### Предварительные требования   <a name="prerequisites"></a>

- **Python 3.10+**  
- **pip** (менеджер пакетов)  
- **Git**  

### Установка  <a name="installation"></a>

1. **Клонируйте репозиторий**  

```sh
git clone https://github.com/ove4lo/online_store
cd online_store
```

2. **Установите зависимости**  

```sh
pip install -r requirements.txt
```

3. **Выполните миграции и создайте суперпользователя**  

```sh
python manage.py migrate
python manage.py createsuperuser
```

4. **Запустите сервер**  

```sh
python manage.py runserver
```

### Использование  <a name="usage"></a>

После запуска сервер доступен по адресу:  
`http://127.0.0.1:8000`  

---

## API Эндпоинты  <a name="api-endpoints"></a>

### Пользователи  

| Метод | Эндпоинт           | Действие |
|-------|--------------------|----------|
| POST  | `/user/register/`  | Регистрация |
| POST  | `/user/login/`     | Вход |
| POST  | `/user/logout/`    | Выход |
| GET   | `/user/current/`   | Текущий пользователь |
| GET   | `/user/{id}/`      | Данные пользователя по ID |
| PATCH | `/user/update/`    | Обновление профиля |

### Товары  

| Метод | Эндпоинт                 | Действие |
|-------|--------------------------|----------|
| GET   | `/products/`             | Все товары |
| GET   | `/products/{id}/`        | Товар по ID |
| POST  | `/products/create/`      | Создание нового товара (админ) |
| POST  | `/products/edit/{id}/`   | Редактирование товара (админ) |
| DELETE| `/products/soft-delete/{id}/` | Мягкое удаление товара (админ) |
| DELETE| `/products/hard-delete/{id}/` | Полное удаление товара (админ) |

### Категории и бренды  

| Метод | Эндпоинт  | Действие |
|-------|-----------|----------|
| GET   | `/brand/` | Список брендов |
| GET   | `/categories/` | Список категорий |

### Заказы  

| Метод | Эндпоинт                | Действие |
|-------|-------------------------|----------|
| POST  | `/orders/create/`       | Создать заказ |
| GET   | `/orders/`              | Все заказы (админ) |
| GET   | `/orders/{id}/`         | Заказ по ID |
| GET   | `/orders/user/{id}`     | Все заказы пользователя |
| PATCH | `/orders/status/{id}/`  | Обновить статус заказа (админ) |

### Избранное  

| Метод | Эндпоинт                  | Действие |
|-------|---------------------------|----------|
| GET   | `/get_wishlist/`          | Получить избранное |
| POST  | `/add_to_wishlist/`       | Добавить товар в избранное |
| DELETE| `/remove_from_wishlist/{id}/` | Удалить товар из избранного |
| DELETE| `/clear_wishlist/`        | Очистить избранное |

---

[⬆ Вернуться к началу](#top)
