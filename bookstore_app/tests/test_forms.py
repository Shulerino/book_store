from distutils.log import Log
from django.test import TestCase
from bookstore_app.models import *
from bookstore_app.forms import *
from bookstore_app.views import email

class TestSearchForm(TestCase):
    def test_searchform_label(self):
        form=SearchForm()
        self.assertEqual(form.fields["search_title"].label, "Введите название книги")

class TestGenreForm(TestCase):
    def test_genreform_label(self):
        form=GenreForm()
        self.assertEqual(form.fields["genre_list"].label, "Выберете жанр")

class TestAuthorForm(TestCase):
    def test_authorform_label(self):
        form=AuthorForm()
        self.assertEqual(form.fields["author_list"].label, "Выберете автора")

class TestLanguageForm(TestCase):
    def test_languageform_label(self):
        form=LanguageForm()
        self.assertEqual(form.fields["language_list"].label, "Выберете язык")

class TestLoginForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user=User.objects.create(username='user_test')
        cls.user.set_password("1q2w3e4C")
        cls.user.save()
    
    def tearDown(self):
        self.user.delete()

    def test_loginform_label(self):
        form=LoginForm()
        self.assertEqual(form.fields["username"].label, "Логин")
        self.assertEqual(form.fields["password"].label, "Пароль")
    
    def test_loginform_maxlength(self):
        form=LoginForm()
        self.assertEqual(form.fields["username"].max_length, 150)
        self.assertEqual(form.fields["password"].max_length, 20)

    def test_loginform_valid(self):
        form=LoginForm(data={
            'username': 'user_wrong',
            'password': '1q2w3e4C',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'], ['Неправильный логин или пароль'])

    def test_loginform_inactive(self):
        user=User.objects.get(pk=1)
        user.is_active=False
        user.save()
        form=LoginForm(data={
            'username': 'user_test',
            'password': '1q2w3e4C',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'], ['Аккаунт отключен'])

class TestRegisterForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user=User.objects.create(username='user_test', email='user_test@mail.ru')
        cls.user.set_password("1q2w3e4C")
        cls.user.save()
    
    def tearDown(self):
        self.user.delete()

    def test_registerform_label(self):
        form=RegisterForm()
        field_verboses={
            "username": "Логин",
            "password1": "Пароль",
            "password2": "Повторите пароль",
            "first_name": "Имя пользователя",
            "last_name": "Фамилия пользователя",
            "email_address": "E-mail",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(form.fields[field].label, expected_value)

    def test_registerform_maxlength(self):
        form=RegisterForm()
        self.assertEqual(form.fields["username"].max_length, 150)
        self.assertEqual(form.fields["password1"].max_length, 20)
        self.assertEqual(form.fields["password2"].max_length, 20)
        self.assertEqual(form.fields["first_name"].max_length, 30)
        self.assertEqual(form.fields["last_name"].max_length, 150)

    def test_registerform_required(self):
        form=RegisterForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'], ['Поле обязательно для заполнения'])
        self.assertEqual(form.errors['password1'], ['Поле обязательно для заполнения'])
        self.assertEqual(form.errors['password2'], ['Поле обязательно для заполнения'])
        self.assertEqual(form.errors['email_address'], ['Поле обязательно для заполнения'])

    def test_registerform_maxlength(self):
        form=RegisterForm(data={
            'username': 'loginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginnn',
            'password1': '1q2w3e4Cccccccccccccc',
            'password2': '1q2w3e4Cccccccccccccc',
            'first_name': 'qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq',
            'last_name': 'loginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginnnnnnn'
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'], ['Слишком длинный логин'])
        self.assertEqual(form.errors['password1'], ['Слишком большой пароль'])
        self.assertEqual(form.errors['password2'], ['Слишком большой пароль'])
        self.assertEqual(form.errors['first_name'], ['Слишком длинное имя'])
        self.assertEqual(form.errors['last_name'], ['Слишком большая фамилия'])
       

    def test_registerform_unique(self):
        form=RegisterForm(data={
            'username': 'user_test',
            'password1': '1q2w3e4C',
            'password2': '1q2w3e4C',
            "email_address": "user@mail.ru",
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'], ['Пользователь с таким именем уже существует'])

    def test_registerform_password(self):
        form=RegisterForm(data={
            'username': 'user_test1',
            'password1': '1q2w3e4C',
            'password2': '1q2w3e4CCCC',
            "email_address": "user@mail.ru",
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password2'], ['Пароли не совпадают'])

    def test_registerform_email(self):
        form=RegisterForm(data={
            'username': 'user_test1',
            'password1': '1q2w3e4C',
            'password2': '1q2w3e4C',
            "email_address": "userl.ru",
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email_address'], ['Некорректный адрес'])

class TestPasswordForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user=User.objects.create(username='user_test')
        cls.user.set_password("1q2w3e4C")
        cls.user.save()
    
    def tearDown(self):
        self.user.delete()

    def test_passwordform_label(self):
        form=PasswordForm(self.user)
        field_verboses={
            "old_password": "Старый пароль",
            "new_password1": "Новый пароль",
            "new_password2": "Повторите новый пароль",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(form.fields[field].label, expected_value)

    def test_passwordform_maxlength(self):
        form=PasswordForm(self.user)
        self.assertEqual(form.fields["old_password"].max_length, 20)
        self.assertEqual(form.fields["new_password1"].max_length, 20)
        self.assertEqual(form.fields["new_password2"].max_length, 20)

    def test_passwordform_maxlength(self):
        form=PasswordForm(self.user, data={
            'old_password': self.user.password,
            'new_password1': '1q2w3e4Cccccccccccccc',
            'new_password2': '1q2w3e4Cccccccccccccc',
        })
        self.assertEqual(form.errors['new_password1'], ['Слишком большой пароль'])
        self.assertEqual(form.errors['new_password2'], ['Слишком большой пароль'])

    def test_passwordform_wrong(self):
        form=PasswordForm(self.user, data={
            'old_password': '1q2w3e4TTT',
            'new_password1': '1q2w3e4C',
            'new_password2': '1q2w3e4C',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['old_password'], ['Неправильный старый пароль'])

    def test_passwordform_missmatch(self):
        form=PasswordForm(self.user, data={
            'old_password': self.user.password,
            'new_password1': '1q2w3e4C',
            'new_password2': '1q2w3e4Ccc',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['new_password2'], ['Новые пароли не совпадают'])
