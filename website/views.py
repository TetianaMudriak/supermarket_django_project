from django.contrib.postgres.search import SearchVector
from django.views.generic import FormView, ListView
from django.db.models import Q

from supermarket.models import Product
from supermarket import selectors
from .forms import ContactForm
from .models import Contact


class ContactView(FormView):
    template_name = 'contact.html'
    model = Contact
    form_class = ContactForm
    success_url = '/contact-us/'

    def form_valid(self, form):
        Contact.objects.create(**form.cleaned_data)
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


# class SubscribeView(FormView):
#     template_name = 'index.html'
#     model = Subscribe
#     form_class = SubscribeForm
#     success_url = '/index/'
#
#     def form_valid(self, form):
#         Subscribe.objects.create(**form.cleaned_data)
#         return super().form_valid(form)
#
#     def form_invalid(self, form):
#         return super().form_invalid(form)


class SearchView(ListView):
    template_name = 'shop-grid.html'
    model = Product
    context_object_name = 'products'
    paginate_by = 12

    def get(self, request, *args, **kwargs):
        self.search_query = self.request.GET.get('s')
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        # _filter = {
        #     'title__icontains': self.search_query,
        # } # Search only by titles

        # _filter = Q(title__icontains=self.search_query) | Q(
        #     full_description__icontains=self.search_query) | Q(
        #     categories__name__icontains=self.search_query) | Q(
        #     brand__name__icontains=self.search_query) | Q(
        #     manufacturer__name__icontains=self.search_query) | Q(
        #     country__name__icontains=self.search_query
        # ) # Search by many fields using Q

        vector = SearchVector('title', 'categories__name', 'full_description',
                              'brand__name', 'country__name',
                              'manufacturer__name')

        # return Product.objects.prefetch_related('images', 'categories').filter(
        #     **_filter).order_by('id')

        # return Product.objects.prefetch_related('images', 'categories').filter(
        #     _filter).order_by('id')

        return Product.objects.prefetch_related(
            'images', 'categories'
        ).annotate(
            search=vector
        ).filter(
            search=self.search_query
        ).order_by('id')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context |= {
            'search_query': self.search_query,
            'search_result_count': self.get_queryset().count(),
            'category_tabs': selectors.categories_selector(5)
        }
        return context
