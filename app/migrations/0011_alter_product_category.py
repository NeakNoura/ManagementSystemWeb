# Generated by Django 5.1.4 on 2025-02-24 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_alter_product_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.CharField(choices=[('B1', 'Burger-1'), ('B2', 'Burger-2'), ('B3', 'Burger-3'), ('D1', 'Dish-1'), ('D2', 'Dish-2'), ('D3', 'Dish-3'), ('D4', 'Dish-4'), ('D7', 'Dish-5'), ('D7', 'Dish-6'), ('D7', 'Dish-7'), ('D7', 'Dish-8'), ('I1', 'Image-1'), ('I2', 'Image-2'), ('I3', 'Image-3')], max_length=255),
        ),
    ]
