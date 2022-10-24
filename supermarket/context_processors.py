from django.db.models import Count

from . models import Category
from . import selectors


def categories_menu(request):

    return {
        'categories': selectors.categories_selector(6)
    }

