import sys
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import random
import logging

import requests
from bs4 import BeautifulSoup
from django.db.transaction import atomic
from django.utils.text import slugify

from supermarket.models import Product, Category, Image, Brand, Country, \
    Manufacturer

TIME_OUT = 10

logger = logging.getLogger('logit')


def upload_img_to_local_media(
        img_url: str,
        image_name: str,
        product: Product
):
    with requests.Session() as session:
        img_response = session.get(img_url, timeout=TIME_OUT)

    with open(f'media/images/{image_name}', 'wb') as file:
        file.write(img_response.content)

    Image.objects.create(
        product=product,
        image=f'images/{image_name}',
        base_url=img_url,
    )


@atomic
def process(html_string: str, url: str):
    soup = BeautifulSoup(html_string, 'html.parser')

    try:
        brand = soup.select('[data-marker~=tm]')
        brand = brand[0].select('.BigProductCardDescription__link')
        brand = brand[0].text.strip().capitalize()
        brand, _ = Brand.objects.get_or_create(name=brand)

        country = soup.select('[data-marker~=country]')
        if country:
            country = country[0].select(
                '.BigProductCardDescription__entryValue')
            country = country[0].text.strip()
        else:
            country = "No info"

        country, _ = Country.objects.get_or_create(name=country)

        manufacturer = soup.select('[data-marker~=pr]')

        if not manufacturer:
            manufacturer = 'No info'
        else:
            manufacturer = manufacturer[0].select(
                '.BigProductCardDescription__entryValue')
            manufacturer = manufacturer[0].text.strip().capitalize()

        manufacturer, _ = Manufacturer.objects.get_or_create(name=manufacturer)

        title = soup.select('.BigProductCardTopInfo__title')
        price = soup.select('.Price__value_title')
        price = round(float(price[0].text.strip()), 2)
        content = soup.select('.BigProductCardDescription__section')
        desc_data = {}
        desc_titles = []
        desc_values = []
        availability = soup.select('.AddButton__text')
        availability = True if availability[
                                   0].text.strip() == "Add to cart" else False

        for elem in content:
            desc_heading = elem.select('.BigProductCardDescription__heading')[
                0].text.strip()
            for item in elem.select('.BigProductCardDescription__infoEntry'):
                desc_title = \
                    item.select('.BigProductCardDescription__entryTitle')[
                        0].text.strip()
                desc_titles.append(desc_title)
                desc_value = \
                    item.select('.BigProductCardDescription__entryValue')[
                        0].text.strip()
                desc_values.append(desc_value)

            desc_data[desc_heading] = {desc_titles[i]: desc_values[i] for i in
                                       range(len(desc_titles))}

            desc_titles.clear()
            desc_values.clear()

        description = []
        for key, value in desc_data.items():
            description.append(f'<p> {key} </p>')
            for key1, value1 in value.items():
                description.append(f'<p> {key1} - {value1} </p>')

        description = " ".join(description)

        sale = [5, 10, 15, 20, 30, 50]

        product, _ = Product.objects.get_or_create(
            slug=slugify(title := title[0].text.strip()),
            defaults={
                'base_url': url,
                'title': title,
                'price': price,
                'old_price': price * 100 / (100 - random.choice(sale)),
                'short_description': description[:100] + "...",
                'full_description': description,
                'availability': availability,
                'brand': brand,
                'country': country,
                'manufacturer': manufacturer,
            }
        )

        categories = soup.select('.BigProductCardDescription__link')[0]
        categories = categories.get('href').split('/')
        categories = categories[3]
        categories = categories.replace('-metro', '')
        category_slug = categories

        categories = categories.split('-')
        categories = ' '.join(categories).capitalize()

        categories, _ = Category.objects.get_or_create(name=categories,
                                                       slug=category_slug)
        product.categories.add(categories)

        images = soup.select('.ProductImagesGallery__noZoomImage')
        images = [img.get('src') for img in images]

        image_names = soup.select('.ProductImagesGallery__noZoomImage')
        image_names = [img_name.get('title') for img_name in image_names]
        image_names = [img_name.split() for img_name in image_names]
        image_names = [('-'.join(img_name) + '.jpeg') for img_name in
                       image_names]

        logger.debug('Uploading image')

        for image, name in zip(images, image_names):
            logger.debug(name)
            upload_img_to_local_media(
                image,
                name.lower(),
                product
            )

        logger.debug('Done!')

    except Exception as error:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(f'Parsing Error {error}, {exc_tb.tb_linenof}')


def worker(queue: Queue):
    while True:
        url = queue.get()
        logger.debug(f'[WORKING ON], {url}')
        try:
            with requests.Session() as session:
                response = session.get(
                    url,
                    allow_redirects=True,
                    timeout=TIME_OUT
                )
                logger.debug(response.status_code)

                if response.status_code == 404:
                    logger.debug(f'Page not found {url}')
                    break

                assert response.status_code in (200, 301, 302), "Bad response"

            process(response.text, url)

        except (
                requests.Timeout,
                requests.TooManyRedirects,
                requests.ConnectionError,
                requests.RequestException,
                requests.ConnectTimeout,
                AssertionError
        ) as error:
            logger.error(f'An error happen {error}')
            queue.put(url)

        if queue.qsize() == 0:
            break


def main():
    category_urls = ['https://metro.zakaz.ua/en/categories/vegetables-metro/',
                     'https://metro.zakaz.ua/en/categories/fruits-metro/',
                     'https://metro.zakaz.ua/en/categories/dried-fruits-metro/',
                     'https://metro.zakaz.ua/en/categories/exotic-fruits-metro/',
                     'https://metro.zakaz.ua/en/categories/mushrooms-metro/',
                     'https://metro.zakaz.ua/en/categories/fresh-greens-metro/']

    i = 0

    while i < len(category_urls):
        with requests.Session() as links_session:
            response = links_session.get(category_urls[i])

        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.select('.ProductsBox .ProductTile')
        links = [link.get('href') for link in links]

        queue = Queue()

        for url in links[0:]:
            queue.put(f'https://metro.zakaz.ua{url}')

        worker_number = 20

        with ThreadPoolExecutor(max_workers=worker_number) as executor:
            for _ in range(worker_number):
                executor.submit(worker, queue)

        i += 1


if __name__ == '__main__':
    main()
