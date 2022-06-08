# Generated by Django 4.0.4 on 2022-06-08 10:20

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookstore_app', '0025_remove_book_genre_book_genre'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='count',
            field=models.IntegerField(null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='book',
            name='price',
            field=models.IntegerField(null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Стоимость'),
        ),
        migrations.AlterField(
            model_name='rent',
            name='date_return',
            field=models.DateField(default=datetime.date(2022, 6, 22)),
        ),
        migrations.AlterField(
            model_name='rent',
            name='date_start',
            field=models.DateField(default=datetime.date(2022, 6, 8)),
        ),
    ]
