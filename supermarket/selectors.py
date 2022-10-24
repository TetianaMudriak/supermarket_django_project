from random import randint, sample
from django.db.models import Count
from django.shortcuts import get_object_or_404

from . models import Product, Category


def categories_selector(categories_limit: int = 6):
    categories = Category.objects.prefetch_related(
        'products'
    ).annotate(
        products_count=Count('products')
    ).order_by('-products_count')
    return categories[:categories_limit]


def featured_products_by_category_selector(category_position: int,
                                           products_number: int = 4,
                                           ):
    category_name = str(categories_selector()[category_position])

    products = Product.objects.prefetch_related(
        'images', 'categories'
    ).exclude(
        images__image__isnull=False, images__image=''
    ).filter(
        categories__name__contains=category_name
    )

    return products[:products_number]


def new_arrivals_products_selector(prod_limit: int):
    return Product.objects.prefetch_related(
        'images'
    ).exclude(
        images__image__isnull=False, images__image=''
    ).order_by('-date_created')[:prod_limit]


def related_products_selector(product: Product, prod_limit: int = 8):

    related_products = Product.objects.filter(
        categories__id__in=product.categories.all()
    )

    return related_products[:prod_limit]
