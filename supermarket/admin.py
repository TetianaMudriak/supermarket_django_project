from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from django.utils.html import format_html


from . models import Category, Product, Image, Brand, Country, Manufacturer


class ImageInLineAdmin(admin.TabularInline):
    model = Image
    fields = ('picture', 'image')
    readonly_fields = fields
    extra = 0

    @staticmethod
    def picture(obj):
        return format_html(
            '<img src="{}" style="max-width: 50px">', obj.image.url
        )


class ProductAdmin(SummernoteModelAdmin):
    summernote_fields = ('short_description', 'full_description')
    inlines = (ImageInLineAdmin,)
    list_display = ('title', 'price', 'old_price', 'availability')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title',)
    list_filter = ('brand', 'country')
    list_editable = ('availability',)

    fieldsets = (
        (None, {
            'fields': (
                'base_url',
                ('title', 'slug'),
                ('short_description',),
                ('full_description',),
                ('price',),
                ('old_price',),
                ('availability',),
                ('categories', 'brand'),
                ('country', 'manufacturer'),
            )
        }),
    )


class ImageAdmin(admin.ModelAdmin):
    list_display = ('picture',)

    @staticmethod
    def picture(obj):
        return format_html(
            '<img src="{}" style="max-width: 50px">', obj.image.url
        )


class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_products')
    search_fields = ('name',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('products')

    @staticmethod
    def total_products(obj):
        count = obj.products.count()
        link = f'/admin/supermarket/product/?brand__id__exact={obj.id}'
        return format_html(f'<a href="{link}">{count} products</a>')


class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_products')
    search_fields = ('name',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('products')

    @staticmethod
    def total_products(obj):
        count = obj.products.count()
        link = f'/admin/supermarket/product/?country__id__exact={obj.id}'
        return format_html(f'<a href="{link}">{count} products</a>')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_products')
    search_fields = ('name',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('products')

    @staticmethod
    def total_products(obj):
        count = obj.products.count()
        link = f'/admin/supermarket/product/?categories__id__exact={obj.id}'
        return format_html(f'<a href="{link}">{count} products</a>')


class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_products')
    search_fields = ('name',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('products')

    @staticmethod
    def total_products(obj):
        count = obj.products.count()
        link = f'/admin/supermarket/product/?manufacturer__id__exact={obj.id}'
        return format_html(f'<a href="{link}">{count} products</a>')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Manufacturer, ManufacturerAdmin)
admin.site.register(Image, ImageAdmin)


