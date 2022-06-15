# Generated by Django 4.0.4 on 2022-06-15 18:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookstore_app', '0034_remove_book_genre_book_genre_alter_book_language'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='genre',
            field=models.CharField(choices=[('Basnya', 'Басня'), ('Povest', 'Повесть'), ('Poema', 'Поэма'), ('Proza', 'Проза'), ('Pyesa', 'Пьеса'), ('Rasskaz', 'Рассказ'), ('Roman', 'Роман'), ('Skazka', 'Сказка'), ('Stix', 'Стихотворение')], max_length=20, verbose_name='Жанр'),
        ),
    ]
