from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='category/images', null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Image(models.Model):
    product = models.ForeignKey(
        'supermarket.Product', on_delete=models.CASCADE, related_name='images'
    )
    image = models.ImageField(upload_to='images', null=True)
    base_url = models.URLField()

    def __str__(self):
        return self.image.url


class Brand(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name


class Manufacturer(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    base_url = models.URLField()
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default='')
    old_price = models.DecimalField(max_digits=10, decimal_places=2, default='')
    short_description = models.CharField(max_length=1000, default='')
    full_description = models.CharField(max_length=5000, default='')
    availability = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    categories = models.ManyToManyField(Category, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='products')
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, related_name='products')

    def __str__(self):
        return self.title
