from email.policy import default
from django import forms
from .models import Author, Genre, Language
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.contrib.auth.models import User


class SearchForm(forms.Form):
    search_title=forms.CharField(required=False, label="Введите название книги")

class GenreForm(forms.Form):
    genre_list=forms.ModelChoiceField(Genre.objects.all(), label="Выберете жанр", required=False)

class AuthorForm(forms.Form):
    author_list=forms.ModelChoiceField(Author.objects.all(), label="Выберете автора", required=False)

class LanguageForm(forms.Form):
    language_list=forms.ModelMultipleChoiceField(queryset=Language.objects.all(), label="Выберете язык", required=False)

class LoginForm(AuthenticationForm):
    username=forms.CharField(max_length=50, label="Логин", required=False)
    password=forms.CharField(max_length=20, label="Пароль", required=False, widget=forms.PasswordInput)
    error_messages = {
        'invalid_login': 'Неправильный логин или пароль',
        'inactive': 'Аккаунт отключен',
    }

class RegisterForm(UserCreationForm):
    username=forms.CharField(max_length=50, label="Логин", required=True)
    password1=forms.CharField(max_length=20, label="Пароль", required=True, widget=forms.PasswordInput)
    password2=forms.CharField(max_length=20, label="Повторите пароль", required=True, widget=forms.PasswordInput)
    first_name=forms.CharField(max_length=50, label="Имя пользователя", required=False)
    last_name=forms.CharField(max_length=50, label="Фамилия пользователя", required=False)
    email_address=forms.EmailField(label="E-mail", required=False)

class UserUpdateForm(forms.Form):
    first_name=forms.CharField(max_length=50, label="Имя пользователя", required=True)
    last_name=forms.CharField(max_length=50, label="Фамилия пользователя", required=True)
    email_address=forms.EmailField(label="E-mail", required=True)

class EmailForm(forms.Form):
    address=forms.ModelMultipleChoiceField(queryset=User.objects.all(), label="Выеберете адресата")
    subject=forms.CharField(max_length=50, label="Тема", required=False)
    message=forms.CharField(max_length=1000, label="Сообщение", widget=forms.Textarea)

class MoneyPlusForm(forms.Form):
    plus=forms.IntegerField(min_value=0, label="Введите сумму")
