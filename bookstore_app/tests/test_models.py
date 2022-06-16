from django.test import TestCase
from bookstore_app.models import *

class AuthorModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Author.objects.create(
            surname="Крылов",
            name="Иван",
            patronymic="Андреевич",
            date_of_birth="1769-02-13",
            date_of_death="1744-11-21"
        )
        Author.objects.create(
            surname="Твен",
            name="Марк",
            date_of_birth="1835-11-30",
            date_of_death="1910-04-21"
        )

    def test_author_label(self):
        author=Author.objects.get(id=1)
        label_surname=author._meta.get_field("surname").verbose_name
        label_name=author._meta.get_field("name").verbose_name
        label_patronymic=author._meta.get_field("patronymic").verbose_name
        label_date_of_birth=author._meta.get_field("date_of_birth").verbose_name
        label_date_of_death=author._meta.get_field("date_of_death").verbose_name
        self.assertEquals(label_surname, "Фамилия")
        self.assertEquals(label_name, "Имя")
        self.assertEquals(label_patronymic, "Отчество")
        self.assertEquals(label_date_of_birth, "Дата рождения")
        self.assertEquals(label_date_of_death, "Дата смерти")

    def test_author_max_length(self):
        author=Author.objects.get(id=1)
        max_length_surname=author._meta.get_field("surname").max_length
        max_length_name=author._meta.get_field("name").max_length
        max_length_patronymic=author._meta.get_field("patronymic").max_length
        self.assertEquals(max_length_surname, 50)
        self.assertEquals(max_length_name, 50)
        self.assertEquals(max_length_patronymic, 50)
    
    def test_author_object_name(self):
        author1=Author.objects.get(id=1)
        author2=Author.objects.get(id=2)
        object_name1=author1.surname + " " + author1.name[0] + "." + author1.patronymic[0] + "."
        object_name2=author2.surname + " " + author2.name[0] + "."
        self.assertEquals(object_name1, str(author1))
        self.assertEquals(object_name2, str(author2))

    def test_author_valid_date(self):
        with self.assertRaises(ValidationError):
            author=Author.objects.get(id=1)
            author.clean()

class BookModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Book.objects.create(
            title="Мертвые души",
            language="RUS",
            genre="Roman",
            price=50,
            count=10
        )
    
    def test_book_label(self):
        book=Book.objects.get(id=1)
        field_verboses={
            "title": "Название",
            "image": "Изображение",
            "summary": "Описание",
            "author": "Автор",
            "language": "Язык",
            "genre": "Жанр",
            "price": "Стоимость",
            "count": "Количество"
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(book._meta.get_field(field).verbose_name, expected_value)

    def test_book_max_length(self):
        book=Book.objects.get(id=1)
        max_length_title=book._meta.get_field("title").max_length
        max_length_summary=book._meta.get_field("summary").max_length
        max_length_language=book._meta.get_field("language").max_length
        max_length_genre=book._meta.get_field("genre").max_length
        self.assertEquals(max_length_title, 100)
        self.assertEquals(max_length_summary, 500)
        self.assertEquals(max_length_language, 3)
        self.assertEquals(max_length_genre, 20)

    def test_book_get_absolute_url(self):
        book=Book.objects.get(id=1)
        self.assertEquals(book.get_absolute_url(),'/book/1')

 
class UserMoneyModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user=User.objects.create(username='user_test', password='1q2w3e4C', email='user_test@mail.com')
        cls.user.save()
        UserMoney.objects.create(
            user=cls.user,
        )

    def tearDown(self):
        self.user.delete()
    
    def test_user_money_label(self):
        usermoney=UserMoney.objects.get(id=1)
        label_money=usermoney._meta.get_field("money").verbose_name
        self.assertEquals(label_money, "Баланс")
    
    def test_user_money_default(self):
        usermoney=UserMoney.objects.get(id=1)
        default_money=usermoney.money
        self.assertEquals(default_money, 0)

    def test_user_money_object_name(self):
        usermoney=UserMoney.objects.get(id=1)
        object_name=usermoney.user.username + " (баланс: {0})".format(str(usermoney.money))
        self.assertEquals(object_name, str(usermoney))
        
class BuyModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user=User.objects.create(username='user_test', password='1q2w3e4C', email='user_test@mail.com')
        cls.user.save()
        cls.book=Book.objects.create(
            title="Мертвые души",
            language="RUS",
            genre="Roman",
            price=50,
            count=10
        )
        Buy.objects.create(
            user=cls.user,
            book=cls.book
        )

    def tearDown(self):
        self.user.delete()
        self.book.delete()

    def test_buy_object_name(self):
        buy=Buy.objects.get(id=1)
        object_name='{0}: {1} {2}'.format(buy.id, buy.user.username, buy.book.title)
        self.assertEquals(object_name, str(buy))

class RentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user=User.objects.create(username='user_test', password='1q2w3e4C', email='user_test@mail.com')
        cls.user.save()
        cls.book=Book.objects.create(
            title="Мертвые души",
            language="RUS",
            genre="Roman",
            price=50,
            count=10
        )
        Rent.objects.create(
            user=cls.user,
            book=cls.book
        )

    def tearDown(self):
        self.user.delete()
        self.book.delete()

    def test_rent_date_today(self):
        rent=Rent.objects.get(id=1)
        today=rent.date_start
        day_return=rent.date_return
        self.assertEquals(today, date.today())
        self.assertEquals(day_return, date.today()+timedelta(14))
    
    def test_rent_object_name(self):
        rent=Rent.objects.get(id=1)
        object_name='{0}: {1} {2} {3}--{4}'.format(rent.id, rent.user.username, rent.book.title, rent.date_start, rent.date_return)
        self.assertEquals(object_name, str(rent))

    def test_rent_return(self):
        rent=Rent.objects.get(id=1)
        days=rent.day_of_return()
        current_days=rent.date_return-date.today()
        self.assertEquals(days, current_days.days)