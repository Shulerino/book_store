from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import datetime, timedelta, timezone, date
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class UserMoney(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    money=models.IntegerField(default=0, validators=[MinValueValidator(0)], null=True, verbose_name="Баланс")

    def __str__(self):
        return self.user.username + " (баланс: {0})".format(str(self.money))

class Author (models.Model):
    surname=models.CharField(max_length=50)
    name=models.CharField(max_length=50)
    patronymic=models.CharField(max_length=50, blank=True, null=True)
    date_of_birth=models.DateField(blank=True, null=True)
    date_of_death=models.DateField(blank=True, null=True)
    country=models.CharField(max_length=50)

    def __str__(self):
        if self.patronymic == None:
            return self.surname + " " + self.name[0] + "."
        else:
            return self.surname + " " + self.name[0] + "." + self.patronymic[0] + "."

    class Meta:
        ordering=["surname"]

class Genre (models.Model):
    genre=models.CharField(max_length=50)

    def __str__(self):
        return self.genre

    class Meta:
        ordering=["genre"]

class Language (models.Model):
    language=models.CharField(max_length=50)

    def __str__(self):
        return self.language

    class Meta:
        ordering=["language"]

class Book (models.Model):
    title=models.CharField(max_length=100, verbose_name="Название")
    image=models.ImageField(upload_to='media/', blank=True, null=True, verbose_name="Изображение")
    summary=models.TextField(max_length=500, blank=True, null=True, verbose_name="Описание")
    author=models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, verbose_name="Автор")
    genre=models.ManyToManyField(Genre, verbose_name="Жанр")
    language=models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, verbose_name="Язык")
    price=models.IntegerField(default=50, validators=[MinValueValidator(0)], null=True, verbose_name="Стоимость")
    count=models.IntegerField(default=10, validators=[MinValueValidator(0)], null=True, verbose_name="Количество")

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
    





