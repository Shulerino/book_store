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

    def test_loginform_right(self):
        form=LoginForm(data={
            'username': 'user_test',
            'password': '1q2w3e4C',
        })
        self.assertTrue(form.is_valid())

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
            "email": "E-mail",
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

    def test_registerform_right(self):
        form=RegisterForm(data={
            'username': 'user_test1',
            'password1': '1q2w3e4C',
            'password2': '1q2w3e4C',
            'first_name': 'Alex',
            'last_name': 'Titov',
            "email": "user111@mail.ru",
        })
        self.assertTrue(form.is_valid())

    def test_registerform_required(self):
        form=RegisterForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'], ['Поле обязательно для заполнения'])
        self.assertEqual(form.errors['password1'], ['Поле обязательно для заполнения'])
        self.assertEqual(form.errors['password2'], ['Поле обязательно для заполнения'])
        self.assertEqual(form.errors['email'], ['Поле обязательно для заполнения'])

    def test_registerform_wronglength(self):
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
            "email": "user@mail.ru",
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'], ['Пользователь с таким именем уже существует'])

    def test_registerform_password(self):
        form=RegisterForm(data={
            'username': 'user_test1',
            'password1': '1q2w3e4C',
            'password2': '1q2w3e4CCCC',
            "email": "user@mail.ru",
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password2'], ['Пароли не совпадают'])

    def test_registerform_email(self):
        form=RegisterForm(data={
            'username': 'user_test1',
            'password1': '1q2w3e4C',
            'password2': '1q2w3e4C',
            "email": "userl.ru",
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'], ['Некорректный адрес'])
    
    def test_registerform_uniqueemail(self):
        form=RegisterForm(data={
            'username': 'user_test1',
            'password1': '1q2w3e4C',
            'password2': '1q2w3e4C',
            "email": "user_test@mail.ru",
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'], ['Пользователь с таким адресом уже существует'])

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

    def test_passwordform_right(self):
        form=PasswordForm(self.user, data={
            'old_password':  '1q2w3e4C',
            'new_password1': '1qaz2wsxQ',
            'new_password2': '1qaz2wsxQ',
        })
        self.assertTrue(form.is_valid())
        
    def test_passwordform_wronglength(self):
        form=PasswordForm(self.user, data={
            'old_password': '1q2w3e4C',
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
            'old_password': '1q2w3e4C',
            'new_password1': '1q2w3e4C',
            'new_password2': '1q2w3e4Ccc',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['new_password2'], ['Новые пароли не совпадают'])

class TestUserUpdateForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user=User.objects.create(
            username='user_test', 
            first_name='Ivan', 
            last_name='Sorokin',
            email='isorokin@mail.com')
        cls.user.set_password("1q2w3e4C")
        cls.user.save()
    
    def tearDown(self):
        self.user.delete()

    def test_userupdateform_label(self):
        form=UserUpdateForm()
        field_verboses={
            "first_name": "Имя пользователя",
            "last_name": "Фамилия пользователя",
            "email": "E-mail",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(form.fields[field].label, expected_value)

    def test_userupdateform_maxlength(self):
        form=UserUpdateForm()
        self.assertEqual(form.fields["first_name"].max_length, 30)
        self.assertEqual(form.fields["last_name"].max_length, 150)
    
    def test_userupdareform_right(self):
        form=UserUpdateForm(data={
            'first_name': 'Oleg',
            'last_name': 'Popov',
            "email": "olegpopov@mail.ru",
        })
        self.assertTrue(form.is_valid())
    
    def test_userupdateform_wronglength(self):
        form=UserUpdateForm(data={
            'first_name': 'qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq',
            'last_name': 'loginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginloginnnnnnn'
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['first_name'], ['Слишком длинное имя'])
        self.assertEqual(form.errors['last_name'], ['Слишком большая фамилия'])
    
    def test_userupdateform_required(self):
        form=UserUpdateForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'], ['Поле обязательно для заполнения'])

    def test_userupdateform_email(self):
        form=UserUpdateForm(data={
            "email": "userl.ru",
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'], ['Некорректный адрес'])

    def test_userupdateform_uniqueemail(self):
        form=UserUpdateForm(data={
            "email": "isorokin@mail.com",
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'], ['Пользователь с таким адресом уже существует'])

class TestEmailForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.massiv=[]
        cls.user=User.objects.create(
            username='user_test', 
            email='isorokin@mail.com')
        cls.user.set_password("1q2w3e4C")
        cls.user.save()
        cls.massiv.append(cls.user)

    
    def tearDown(self):
        self.user.delete()

    def test_emailform_label(self):
        form=EmailForm()
        field_verboses={
            "address": "Выберете адресата",
            "subject": "Тема",
            "message": "Сообщение",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(form.fields[field].label, expected_value)
    
    def test_emailform_maxlength(self):
        form=EmailForm()
        self.assertEqual(form.fields["subject"].max_length, 50)
        self.assertEqual(form.fields["message"].max_length, 1000)

    def test_emailform_right(self):
        form=EmailForm(data={
            'address': self.massiv,
            'subject': 'Tema',
            "message": "Hello, Django",
        })
        self.assertTrue(form.is_valid())

    def test_emailform_required(self):
        form=EmailForm(data={
            'subject': 'Tema',
            "message": "Hello, Django",
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['address'], ['Поле обязательно для заполнения'])

    def test_emailform_wronglength(self):
        form=EmailForm(data={
            'address': self.massiv,
            'subject': 'TemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTema',
            "message": "TemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTemaTema",
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['subject'], ['Слишком длинная тема'])
        self.assertEqual(form.errors['message'], ['Слишком большое сообщение'])

class TestMoneyPlusForm(TestCase):
    def test_moneyplusform_label(self):
        form=MoneyPlusForm()
        self.assertEqual(form.fields["plus"].label, "Введите сумму")

    def test_moneyplusform_maxlength(self):
        form=MoneyPlusForm()
        self.assertEqual(form.fields["plus"].min_value, 0)
        self.assertEqual(form.fields["plus"].max_value, 2147483647)

    def test_moneyplusform_right(self):
        form=MoneyPlusForm(data={
            'plus': 50,
        })
        self.assertTrue(form.is_valid())

    def test_moneyplusform_wrong(self):
        form=MoneyPlusForm(data={
            'plus': -56,
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['plus'], ['Некорректное значение'])

    def test_moneyplusform_overmax(self):
        form=MoneyPlusForm(data={
            'plus': 4147483647,
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['plus'], ['Слишком большое число'])