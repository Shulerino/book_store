# Generated by Django 4.0.4 on 2022-05-03 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookstore_app', '0005_alter_book_options_alter_genre_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='count',
            field=models.IntegerField(default=10),
        ),
        migrations.AddField(
            model_name='book',
            name='price',
            field=models.IntegerField(default=50),
        ),
    ]
