# Generated by Django 4.1.1 on 2022-10-20 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supermarket', '0002_category_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='image',
            field=models.ImageField(null=True, upload_to='category/images'),
        ),
    ]
