# Generated by Django 5.1.7 on 2025-03-23 19:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_remove_product_sku'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='sku',
            field=models.IntegerField(blank=True, null=True, unique=True),
        ),
    ]
