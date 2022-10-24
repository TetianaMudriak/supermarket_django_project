from . models import Product, Category, Brand, Country, Manufacturer, Image


def clear_product_table():
    return Product.objects.all().delete()


def clear_category_table():
    return Category.objects.all().delete()


def clear_brand_table():
    return Brand.objects.all().delete()


def clear_country_table():
    return Country.objects.all().delete()


def clear_manufacturer_table():
    return Manufacturer.objects.all().delete()


def clear_image_table():
    return Image.objects.all().delete()


def main():
    clear_product_table()
    clear_image_table()
    clear_manufacturer_table()
    clear_brand_table()
    clear_category_table()
    clear_country_table()


if __name__ == '__main__':
    main()
