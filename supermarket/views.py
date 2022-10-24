from random import randint, sample

from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, DetailView, ListView

from . models import Category, Product
from . import selectors


# def index(request):
#     # search_categories = Category.objects.annotate(
#     #     products_count=Count('products')
#     # ).order_by('-products_count')
#
#     # cat_name_1 = str(search_categories[0])
#     # cat_name_2 = str(search_categories[1])
#     # cat_name_3 = str(search_categories[2])
#     # cat_name_4 = str(search_categories[3])
#     # cat_name_5 = str(search_categories[4])
#
#     # cat1 = Product.objects.filter(categories__name__contains=cat_name_1)
#     # cat2 = Product.objects.filter(categories__name__contains=cat_name_2)
#     # cat3 = Product.objects.filter(categories__name__contains=cat_name_3)
#     # cat4 = Product.objects.filter(categories__name__contains=cat_name_4)
#     # cat5 = Product.objects.filter(categories__name__contains=cat_name_5)
#
#     products_count = Product.objects.count()
#
#     min_index = randint(0, Product.objects.count())
#     min_index = min_index if min_index < products_count - 4 else min_index - 4
#     max_index = min_index + 4
#     products = Product.objects.prefetch_related(
#         'images'
#     )
#
#     # cat1 = products.filter(categories__name__contains=cat_name_1)
#     # cat2 = products.filter(categories__name__contains=cat_name_2)
#     # cat3 = products.filter(categories__name__contains=cat_name_3)
#     # cat4 = products.filter(categories__name__contains=cat_name_4)
#     # cat5 = products.filter(categories__name__contains=cat_name_5)
#
#     new_arrivals = Product.objects.prefetch_related(
#         'images'
#     ).order_by('-date_created')[:4]
#
#     context = {
#         # 'categories': search_categories[:6],
#         # 'cat1': cat1[:4],
#         # 'cat2': cat2[:4],
#         # 'cat3': cat3[:4],
#         # 'cat4': cat4[:4],
#         # 'cat5': cat5[:4],
#         'featured_products': products[min_index: max_index],
#         'new_arrivals': new_arrivals
#     }
#     return render(request, 'index.html', context)

class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context |= {
            'featured_categories': selectors.categories_selector(5),
            'cat1': selectors.featured_products_by_category_selector(0),
            'cat2': selectors.featured_products_by_category_selector(1),
            'cat3': selectors.featured_products_by_category_selector(2),
            'cat4': selectors.featured_products_by_category_selector(3),
            'cat5': selectors.featured_products_by_category_selector(4),
            'new_arrivals': selectors.new_arrivals_products_selector(4),
        }
        return context


# def catalogue(request, **kwargs):
#     search_categories = Category.objects.prefetch_related(
#         'products'
#     ).annotate(
#         products_count=Count('products')
#     ).order_by('-products_count')
#
#     category = get_object_or_404(Category, slug=kwargs.get('slug'))
#     products = Product.objects.prefetch_related(
#         'images'
#     ).filter(categories=category)[:12]
#     context = {
#         'products': products,
#         'category_tabs': search_categories[:5]
#     }
#     return render(request, 'shop-grid.html', context)

class CatalogueView(ListView):
    template_name = 'shop-grid.html'
    model = Product
    context_object_name = 'products'
    slug_url_kwarg = 'slug'
    paginate_by = 12

    def get_queryset(self):
        return Product.objects.prefetch_related('images').filter(
            categories__slug=self.kwargs.get('slug'))

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context |= {
            'current_category': self.kwargs.get('slug'),
            'product_count': self.get_queryset().count(),
            'category_tabs': selectors.categories_selector(5)
        }
        return context


# def product(request, **kwargs):
#     item = get_object_or_404(
#         Product.objects.prefetch_related('images', 'categories'),
#         slug=kwargs.get('slug')
#     )
#
#     related_products = Product.objects.filter(
#         categories__id__in=item.categories.all()
#     ).values_list('id', flat=True)
#     random_ids = sample(list(related_products), 8)
#     related_products = Product.objects.prefetch_related(
#         'images', 'categories'
#     ).filter(pk__in=random_ids)
#
#     context = {
#         'product': item,
#         'related_products': related_products,
#     }
#     return render(request, 'product-details.html', context)

class ProductView(DetailView):
    template_name = 'product-details.html'
    model = Product
    context_object_name = 'product'
    slug_url_kwarg = 'slug'
    queryset = Product.objects.prefetch_related('images', 'categories')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context |= {
            'related_products': selectors.related_products_selector(self.object)
        }
        return context



