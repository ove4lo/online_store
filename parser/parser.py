import os
from pathlib import Path

import django
from django.core.files import File

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'online_store.settings')
django.setup()

import requests
import fake_useragent
from selenium import webdriver
from bs4 import BeautifulSoup
import random
import time
import os
import multiprocessing

from django.core.files import File
import os
from product.models import Product, ProductImage
from brand.models import Brand
from category.models import category


def save_to_database(watch_info):
    try:
        if not watch_info or not isinstance(watch_info, dict):
            print("Некорректные данные о товаре")
            return None


        brand_name = watch_info.get('Бренд')
        if not brand_name:
            model_name = watch_info.get('Артикул/модель', '')
            brand_name = model_name.split()[0] if model_name else 'Unknown'

        try:
            brand, _ = Brand.objects.get_or_create(name=brand_name.strip())
        except Exception as e:
            print(f"Ошибка при создании бренда {brand_name}: {str(e)}")
            brand = Brand.objects.first()


        required_fields = ['Артикул/модель', 'Цена']
        for field in required_fields:
            if field not in watch_info or not watch_info[field]:
                print(f"Отсутствует обязательное поле {field}")
                return None

        try:
            price_str = watch_info['Цена'].replace(' ₽', '').replace(' ', '').replace('\xa0', '')
            price = float(price_str)
        except (ValueError, TypeError) as e:
            print(f"Ошибка преобразования цены: {str(e)}")
            price = 0.0  # Устанавливаем цену по умолчанию

        # Создаем продукт
        try:
            product = Product(
                brand=brand,
                name=watch_info['Артикул/модель'],
                price=price,
                country=watch_info.get('Страна', ''),
                movement_type=watch_info.get('Тип механизма', ''),
                case_material=watch_info.get('Корпус', ''),
                water_resistance=watch_info.get('Водозащита', ''),
                glass_type=watch_info.get('Стекло', ''),
                dimensions=watch_info.get('Габаритные размеры', ''),
                description=watch_info.get('Описание', '')
            )
            product.save()
        except Exception as e:
            print(f"Ошибка при создании продукта: {str(e)}")
            return None


        try:
            watch_category, _ = category.objects.get_or_create(name='Часы')
            product.category.add(watch_category)


            for cat_name in watch_info.get('Категории', []):
                if cat_name and cat_name.strip():
                    try:
                        cat, _ = category.objects.get_or_create(name=cat_name.strip())
                        product.category.add(cat)
                    except Exception as e:
                        print(f"Ошибка при добавлении категории {cat_name}: {str(e)}")
                        continue
        except Exception as e:
            print(f"Ошибка при добавлении категорий: {str(e)}")


        for i, image_path in enumerate(watch_info.get('Все фото', [])):
            try:
                if image_path and os.path.exists(image_path):
                    with open(image_path, 'rb') as f:
                        image = ProductImage(
                            product=product,
                            is_main=(i == 0)
                        )
                        image.image.save(os.path.basename(image_path), File(f))
                        image.save()
                else:
                    print(f"Не найдена фотка: {image_path}")
            except Exception as e:
                print(f"Ошибка при добавлении изображения {image_path}: {str(e)}")
                continue

        print(f"Успешно сохранен продукт: {product.name}")
        return product

    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return None


def get_info_about_watch(link):
    time.sleep(random.randint(10, 15))
    try:
        user = fake_useragent.UserAgent().random
        header = {'User-Agent': user}
        response = requests.get(link, headers=header)
        soup = BeautifulSoup(response.text, 'lxml')


        carousel = soup.find('div', class_='product-photos-nav-items')
        all_images = []

        if carousel:

            image_items = carousel.find_all('div', class_='product-photo-nav-item')
            for item in image_items:
                img_tag = item.find('img')
                if img_tag and img_tag.has_attr('src'):
                    img_url = img_tag['src']
                    high_res_url = img_url.replace('/small/', '/big/')
                    all_images.append(high_res_url)

        print("Найдены изображения:", all_images)


        downloaded_images = []
        for i, img_url in enumerate(all_images):
            try:
                filename = Path(r'D:\Project\online_store\media\product_images') / img_url.split('/')[-1]
                filename.parent.mkdir(parents=True, exist_ok=True)
                img_data = requests.get(img_url, headers=header).content
                with open(filename, 'wb') as handler:
                    handler.write(img_data)
                downloaded_images.append(str(filename))
                print(f"Скачано изображение {i + 1}/{len(all_images)}: {filename}")
            except Exception as e:
                print(f"Ошибка при скачивании {img_url}: {str(e)}")


        watch_info = {
            'Артикул/модель': None,
            'Бренд': None,
            'Цена': None,
            'Страна': None,
            'Фото': downloaded_images[0] if downloaded_images else None,
            'Все фото': downloaded_images,
            'Водозащита': None,
            'Стекло': None,
            'Корпус': None,
            'Тип механизма': None,
            'Габаритные размеры': None,
            'Категории': [],
            'Описание': None,  #
            'Ссылка': link
        }


        description_block = soup.find('div', id='descr_main')
        if description_block:

            for hint in description_block.find_all('div', class_='pt-text pt-right js-hintme-this'):
                hint.decompose()


            description_text = description_block.get_text(separator=' ', strip=True)

            description_text = ' '.join(description_text.split())
            watch_info['Описание'] = description_text


        breadcrumbs = soup.find('div', class_='page-heading-breadcrumbs-items')
        if breadcrumbs:
            breadcrumbs_items = breadcrumbs.find_all('a')
            if len(breadcrumbs_items) > 1:

                watch_info['Бренд'] = breadcrumbs_items[1].text.strip()


                categories = [item.text.strip() for item in breadcrumbs_items[2:]]
                watch_info['Категории'] = categories

        image_watch = soup.find_all('img', itemprop='image')
        if image_watch:
            watch_info['Фото'] = image_watch[0]['src']


        clear_soup = soup.find('dl')
        if clear_soup:
            for p_tag in clear_soup.find_all('p'):
                p_tag.extract()
            for p_tag in clear_soup.find_all('div', class_='pt-text pt-right js-hintme-this'):
                p_tag.extract()

            values = clear_soup.find_all('dd')
            values_lst = []
            for i in values:
                values_lst.append(i.text)

            names = soup.find_all('dt')
            names_lst = []
            for i in names:
                names_lst.append(i.text)

            info = {}
            for i in range(min(len(names_lst), len(values_lst))):
                info[names_lst[i]] = values_lst[i]

            for i in watch_info.keys():
                try:
                    if i not in ['Цена', 'Фото', 'Ссылка', 'Бренд', 'Категории', 'Описание']:
                        watch_info[i] = info[i]
                except:
                    continue

        price = soup.find('span', class_='product-price-item product-price-item--current')
        if price:
            watch_info['Цена'] = str(price.text).strip().replace(' Р', ' ₽')
        try:
            if watch_info['Габаритные размеры']:
                watch_info['Габаритные размеры'] = watch_info['Габаритные размеры'].split('мм')[0] + 'мм'
        except:
            pass
        print(watch_info)
        save_to_database(watch_info)
        return watch_info

    except Exception as e:
        print(f"ОШИБКА в блоке получения инфы часов: {str(e)}")
        return None


def get_links_page():
    links_f = []
    for i in range(2, 3):
        driver = webdriver.Chrome()
        driver.get(f'https://www.alltime.ru/watch/?PAGEN_1={i}')

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        for p_tag in soup.find_all('div', 'tovar_banner'):
            p_tag.extract()

        links = soup.find_all('a', class_='catalog-item-link')
        for link in links:
            links_f.append('https://www.alltime.ru' + link.get('href'))
        driver.quit()
        links_f = [i for i in links_f if i.startswith('https://www.alltime.ru/watch/')]
    return links_f


def ti(link):
    p = multiprocessing.Process(target=get_info_about_watch, args=(link,))
    p.start()
    p.join(60)
    if p.is_alive():
        print(f"Timeout!!!")
        p.terminate()
        p.join()


if __name__ == '__main__':
    links = get_links_page()
    print(f"Найдено ссылок: {len(links)}")

    for link in links:
        try:
            print(f"\nОбрабатываю ссылку: {link}")
            ti(link)
        except Exception as e:
            print(f'Ошибка при обработке {link}: {str(e)}')
            continue

        time.sleep(random.uniform(1, 3))
