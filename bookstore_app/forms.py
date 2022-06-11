from email.policy import default
from django import forms
from .models import Author, Genre, Language
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
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
    username=forms.CharField(max_length=50, label="Логин", error_messages = {
        'unique': 'Пользователь с таким именем уже существует',
        'max_length': 'Слишком длинный логин',
    })
    password1=forms.CharField(max_length=50, label="Пароль", widget=forms.PasswordInput, error_messages = {
        'max_length': 'Слишком большой пароль',
    })
    password2=forms.CharField(max_length=20, label="Повторите пароль", widget=forms.PasswordInput, error_messages = {
        'max_length': 'Слишком большой пароль',
    })
    first_name=forms.CharField(max_length=30, label="Имя пользователя", required=False, error_messages = {
        'max_length': 'Слишком длинное имя',
    })
    last_name=forms.CharField(max_length=150, label="Фамилия пользователя", required=False, error_messages = {
        'max_length': 'Слишком большая фамилия',
    })
    email_address=forms.EmailField(label="E-mail", error_messages = {
        'invalid': 'Некорректный адрес',
        'required': 'Поле обязательно для заполнения'
    })
    error_messages = {
        'unique': 'Пользователь с таким именем уже существует',
        'password_mismatch': 'Пароли не совпадают',
    }

class PasswordForm(PasswordChangeForm):
    old_password=forms.CharField(max_length=50, label="Старый пароль", strip=False, widget=forms.PasswordInput, error_messages = {
        'max_length': 'Слишком большой пароль',
    })
    new_password1=forms.CharField(max_length=50, label="Новый пароль", strip=False, widget=forms.PasswordInput, error_messages = {
        'max_length': 'Слишком большой пароль',
    })
    new_password2=forms.CharField(max_length=20, label="Повторите новый пароль", strip=False, widget=forms.PasswordInput, error_messages = {
        'max_length': 'Слишком большой пароль',
    })
    error_messages = {
        'password_incorrect': "Неправильный старый пароль",
        'password_mismatch': "Новые пароли не совпадают",
        'password_too_common': "Слишком простой пароль",
        'password_too_short': "Слишком короткий пароль. Должно быть минимум 8 символов"
    }

class UserUpdateForm(forms.Form):
    first_name=forms.CharField(max_length=30, label="Имя пользователя", required=False, error_messages = {
        'max_length': 'Слишком длинное имя',
    })
    last_name=forms.CharField(max_length=150, label="Фамилия пользователя", required=False, error_messages = {
        'max_length': 'Слишком большая фамилия',
    })
    email_address=forms.EmailField(label="E-mail", error_messages = {
        'invalid': 'Некорректный адрес',
        'required': 'Поле обязательно для заполнения'
    })

class EmailForm(forms.Form):
    address=forms.ModelMultipleChoiceField(queryset=User.objects.all(), label="Выеберете адресата")
    subject=forms.CharField(max_length=50, label="Тема", required=False)
    message=forms.CharField(max_length=1000, label="Сообщение", widget=forms.Textarea)

class MoneyPlusForm(forms.Form):
    plus=forms.IntegerField(min_value=0, max_value=2147483647, label="Введите сумму", error_messages={
                    'required': 'Поле обязательно для заполнения',
                    'min_value': 'Некорректное значение',
                    'max_value': 'Слишком большое число'
        })
