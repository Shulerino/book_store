# Generated by Django 4.0.4 on 2022-05-07 09:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookstore_app', '0009_rent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rent',
            name='date_return',
            field=models.DateField(default=datetime.datetime(2022, 5, 21, 12, 11, 19, 883124)),
        ),
        migrations.AlterField(
            model_name='rent',
            name='date_start',
            field=models.DateField(default=datetime.datetime(2022, 5, 7, 12, 11, 19, 883097)),
        ),
    ]
