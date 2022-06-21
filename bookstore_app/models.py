from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import timedelta, date
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from ast import literal_eval

# Create your models here.


class UserMoney(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    money=models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(2147483647)], null=True, verbose_name="Баланс")

    def __str__(self):
        return self.user.username + " (баланс: {0})".format(str(self.money))

class Author (models.Model):
    surname=models.CharField(max_length=50, verbose_name="Фамилия")
    name=models.CharField(max_length=50, verbose_name="Имя")
    patronymic=models.CharField(max_length=50, blank=True, null=True, verbose_name="Отчество")
    date_of_birth=models.DateField(blank=True, default='1900-01-01', verbose_name="Дата рождения")
    date_of_death=models.DateField(blank=True, null=True, verbose_name="Дата смерти")

    def __str__(self):
        if self.patronymic == None:
            return "{0} {1}.".format(self.surname, self.name[0])
        else:
            return "{0} {1}.{2}.".format(self.surname, self.name[0], self.patronymic[0])
    class Meta:
        ordering=["surname"]

    def clean(self, *args, **kwargs):
        if self.date_of_death is not None:
            if self.date_of_death < self.date_of_birth:
                raise ValidationError('Дата смерти не может быть раньше даты рождения', code='invalid_death')


class Book (models.Model):
    LANG_CORT=(("ENG", "Английский"), ("DEU", "Немецкий"), ("FRA" ,"Французский"), ("RUS" ,"Русский"), ("ITA", "Итальянский"), ("SPA", "Испанский"), ("CHI", "Китайский"))
    GENR_CORT=((None, "---------"), ("Basnya", "Басня"), ("Povest", "Повесть"), ("Poema", "Поэма"), ("Proza", "Проза"), ("Pyesa", "Пьеса"), ("Rasskaz", "Рассказ"), ("Roman", "Роман"), ("Skazka", "Сказка"), ("Stix", "Стихотворение"))

    title=models.CharField(max_length=100, verbose_name="Название")
    image=models.ImageField(upload_to='media/', blank=True, null=True, verbose_name="Изображение")
    summary=models.TextField(max_length=500, blank=True, null=True, verbose_name="Описание")
    author=models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, verbose_name="Автор")
    language=models.CharField(max_length=3, choices=sorted(LANG_CORT, key=lambda x: x[1] ), verbose_name="Язык")
    genre=models.CharField(max_length=20, choices=sorted(GENR_CORT, key=lambda x: x[1] ), verbose_name="Жанр")
    price=models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(2147483647)], null=True, verbose_name="Стоимость")
    count=models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(2147483647)], null=True, verbose_name="Количество")

    def __str__(self):
        return self.title

    class Meta:
        ordering=["title"]

    def get_absolute_url(self):
        return reverse ("book_info", args=[str(self.id)])


class Buy (models.Model):
    user=models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    book=models.ForeignKey(Book, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return '{0}: {1} {2}'.format(self.id, self.user.username, self.book.title)

class Rent (models.Model):
    user=models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    book=models.ForeignKey(Book, on_delete=models.SET_NULL, null=True)
    date_start=models.DateField(default=date.today())
    date_return=models.DateField(default=date.today()+timedelta(14))

    def __str__(self):
        return '{0}: {1} {2} {3}--{4}'.format(self.id, self.user.username, self.book.title, self.date_start, self.date_return)

    def day_of_return(self):
        data=self.date_return-date.today()
        return data.days
    





