from urllib import response
import django
from django.conf import settings
from django.test import TestCase, override_settings
from bookstore_app.models import *
from bookstore_app.forms import *
from django.contrib.auth.models import User, Group, Permission
from unittest import mock
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
import io
from PIL import Image

def create_image(name_image):
    bts=io.BytesIO()
    img=Image.new("RGB", (100, 100))
    img.save(bts, 'jpeg')
    return SimpleUploadedFile(name=name_image, content=bts.getvalue())


class TestIndex(TestCase):
    @classmethod
    def setUpTestData(cls):
        for num in range(6):
            Author.objects.create(
                surname="surname{0}".format(num+1),
                name="name{0}".format(num+1)
            )

        for num in range(5):
            Book.objects.create(
                title="title{0}".format(num+1),
                author=Author.objects.get(id=num+1),
                genre=Book.GENR_CORT[num+1][0],
                language=Book.LANG_CORT[num+1][0],
            )
        

    def test_index_view_get(self):
        resp1 = self.client.get('')
        resp2 = self.client.get(reverse('index')) 
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp2.status_code, 200)
        self.assertTemplateUsed(resp1, 'index.html')
        
    def test_index_view_post(self):
        resp1 = self.client.post('')
        resp2 = self.client.post(reverse('index')) 
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp2.status_code, 200)
        self.assertTemplateUsed(resp1, 'index.html')
    
    def test_index_view_context(self):
        resp = self.client.get(reverse('index')) 
        self.assertEqual(resp.context["books"], None)
        self.assertIn("author_form", resp.context)
        self.assertIn("genre_form", resp.context)
        self.assertIn("language_form", resp.context)
        self.assertIn("search_form", resp.context)
        self.assertEqual(resp.context["message"], "Выберете книгу")
        
    def test_index_search_right(self):
        books=Book.objects.filter(title__icontains="title")
        resp = self.client.post(reverse('index'), {
            "butsearchtitle": True,
            "search_title": "title",
            })
        self.assertQuerysetEqual(resp.context["books"], books)
    
    def test_index_search_clean(self):
        resp = self.client.post(reverse('index'), {
            "butsearchtitle": True,
            "search_title": "",
            })
        self.assertEqual(resp.context["message"], "Уточните запрос")

    def test_index_search_wrong(self):
        resp = self.client.post(reverse('index'), {
            "butsearchtitle": True,
            "search_title": "wrong",
            })
        self.assertEqual(resp.context["message"], "Книги не найдены")
    
    def test_index_author(self):
        books=Book.objects.filter(author=1)
        resp1 = self.client.post(reverse('index'), {
            "butsearchauthor": True,
            "author_list": 1,
            })
        resp2 = self.client.post(reverse('index'), {
            "butsearchauthor": True,
            "author_list": 6,
            })
        self.assertQuerysetEqual(resp1.context["books"], books)
        self.assertFalse(resp2.context["books"].exists())
        self.assertEqual(resp2.context["message"], "Книги не найдены")
    
    def test_index_genre(self):
        books=Book.objects.filter(genre="Basnya")
        resp1 = self.client.post(reverse('index'), {
            "butsearchauthor": True,
            "genre_list": "Basnya",
            })
        resp2 = self.client.post(reverse('index'), {
            "butsearchauthor": True,
            "genre_list": "Rasskaz",
            })
        self.assertQuerysetEqual(resp1.context["books"], books)
        self.assertFalse(resp2.context["books"].exists())
        self.assertEqual(resp2.context["message"], "Книги не найдены")
    
    def test_index_author_genre(self):
        books=Book.objects.filter(author=1, genre="Basnya")
        resp1 = self.client.post(reverse('index'), {
            "butsearchauthor": True,
            "author_list": 1,
            "genre_list": "Basnya",
            })
        resp2 = self.client.post(reverse('index'), {
            "butsearchauthor": True,
            "author_list": 1,
            "genre_list": "Rasskaz",
            })
        self.assertQuerysetEqual(resp1.context["books"], books)
        self.assertFalse(resp2.context["books"].exists())
        self.assertEqual(resp2.context["message"], "Книги не найдены")
    
    def test_index_language(self):
        books=Book.objects.filter(language__in=["DEU", "ITA"])
        resp1 = self.client.post(reverse('index'), {
            "butsearchlanguage": True,
            "language_list": ["DEU", "ITA"],
            })
        resp2 = self.client.post(reverse('index'), {
            "butsearchauthor": True,
            "language_list": ["ENG"],
            })
        self.assertQuerysetEqual(resp1.context["books"], books)
        self.assertFalse(resp2.context["books"].exists())
        self.assertEqual(resp2.context["message"], "Книги не найдены")


import tempfile
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TestBookDetailView(TestCase):
    @classmethod
    def setUpTestData(cls):
        image_list=[]
        for num in range(5):
            image=mock.MagicMock(spec=File)
            image.name="image{0}.jpg".format(num+1)
            image_list.append(image)
        
        for num in range(6):
            Author.objects.create(
                surname="surname{0}".format(num),
                name="name{0}".format(num)
            )

        for num in range(5):
            Book.objects.create(
                title="title{0}".format(num+1),
                image=image_list[num],
                summary="summary{0}".format(num+1),
                author=Author.objects.get(id=num+1),
                genre=Book.GENR_CORT[num+1][0],
                language=Book.LANG_CORT[num+1][0],
                price=num+101,
                count=num+1
            )

    def test_bookdetail_view_get(self):
        book=Book.objects.get(id=1)
        resp1 = self.client.get('/book/1')
        resp2 = self.client.get('/book/105')
        resp3 = self.client.get(reverse("book_info", kwargs={'pk': 1}))
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp2.status_code, 404)
        self.assertEqual(resp3.status_code, 200)
        self.assertTemplateUsed(resp1, "book_info.html")
        self.assertIn(book.title, resp1.context["book"].title)
        self.assertEqual(book.image, resp1.context["book"].image)
        self.assertIn(book.summary, resp1.context["book"].summary)
        self.assertEqual(book.author, resp1.context["book"].author)
        self.assertIn(book.genre, resp1.context["book"].genre)
        self.assertIn(book.language, resp1.context["book"].language)
        self.assertEqual(book.price, resp1.context["book"].price)
        self.assertEqual(book.count, resp1.context["book"].count)

@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TestBookEditView(TestCase):
    @classmethod
    def setUpTestData(cls):
        image_list=[]
        for num in range(5):
            image=mock.MagicMock(spec=File)
            image.name="image{0}.jpg".format(num+1)
            image_list.append(image)

        user = User.objects.create_user(
            username='user1', 
            password='1q2w3e4C'
            )
        user.save()  
        
        worker = User.objects.create_user(
            username='worker1', 
            password='1q2w3e4C'
            )
        worker.save()
        worker.user_permissions.add(Permission.objects.get(codename='change_book'))

        for num in range(6):
            Author.objects.create(
                surname="surname{0}".format(num),
                name="name{0}".format(num)
            )

        for num in range(5):
            Book.objects.create(
                title="title{0}".format(num+1),
                image=image_list[num],
                summary="summary{0}".format(num+1),
                author=Author.objects.get(id=num+1),
                genre=Book.GENR_CORT[num+1][0],
                language=Book.LANG_CORT[num+1][0],
                price=num+101,
                count=num+1
            )

    def test_bookedit_view_get_right(self):
        book=Book.objects.get(id=1)
        self.client.login(username='worker1', password='1q2w3e4C')
        resp1 = self.client.get('/book/1/update')
        resp2 = self.client.get('/book/105/update')
        resp3 = self.client.get(reverse("book_update", kwargs={'pk': 1}))
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp2.status_code, 404)
        self.assertEqual(resp3.status_code, 200)
        self.assertTemplateUsed(resp1, "book_edit.html")
        self.assertIn(book.title, resp1.context["book"].title)
        self.assertEqual(book.image, resp1.context["book"].image)
        self.assertIn(book.summary, resp1.context["book"].summary)
        self.assertEqual(book.author, resp1.context["book"].author)
        self.assertIn(book.genre, resp1.context["book"].genre)
        self.assertIn(book.language, resp1.context["book"].language)
        self.assertEqual(book.price, resp1.context["book"].price)
        self.assertEqual(book.count, resp1.context["book"].count)
    
    def test_bookedit_view_get_wrong(self):
        self.client.login(username='user1', password='1q2w3e4C')
        resp = self.client.get('/book/1/update')
        self.assertEqual(resp.status_code, 403)

    def test_bookedit_view_post(self):
        self.client.login(username='worker1', password='1q2w3e4C')
        resp = self.client.post(reverse('book_update', kwargs={'pk': 1}), {
            "title": "new_title",
            "image": create_image("test_image.jpg"),
            "summary": "new_summary",
            "author": 3,
            "genre": "Rasskaz",
            "language": "ITA",
            "price": 1000000,
            "count": 500
            })
        self.assertRedirects(resp, reverse('book_info', kwargs={'pk': 1}))
        book=Book.objects.get(id=1)
        author=Author.objects.get(id=3)
        self.assertEqual(book.title, "new_title")
        self.assertEqual(book.image, "media/test_image.jpg")
        self.assertEqual(book.summary, "new_summary")
        self.assertEqual(book.author, author)
        self.assertEqual(book.genre, "Rasskaz")
        self.assertEqual(book.language, "ITA")
        self.assertEqual(book.price, 1000000)
        self.assertEqual(book.count, 500)
    
    def test_bookedit_view_post_required(self):
        self.client.login(username='worker1', password='1q2w3e4C')
        resp = self.client.post(reverse('book_update', kwargs={'pk': 1}), {})
        self.assertFormError(resp, "form", "title", 'Поле обязательно для заполнения')
        self.assertFormError(resp, "form", "author", 'Поле обязательно для заполнения')
        self.assertFormError(resp, "form", "genre", 'Поле обязательно для заполнения')
        self.assertFormError(resp, "form", "language", 'Поле обязательно для заполнения')
        self.assertFormError(resp, "form", "price", 'Поле обязательно для заполнения')
        self.assertFormError(resp, "form", "count", 'Поле обязательно для заполнения')

    def test_bookedit_view_post_minvalue(self):
        self.client.login(username='worker1', password='1q2w3e4C')
        resp = self.client.post(reverse('book_update', kwargs={'pk': 1}), {
            "title": "new_title",
            "summary": "new_summary",
            "author": 3,
            "genre": "Rasskaz",
            "language": "ITA",
            "price": -1000000,
            "count": -500
            })
        self.assertFormError(resp, "form", "price", 'Некорректное значение')
        self.assertFormError(resp, "form", "count", 'Некорректное значение')

    def test_bookedit_view_post_maxvalue(self):
        self.client.login(username='worker1', password='1q2w3e4C')
        resp = self.client.post(reverse('book_update', kwargs={'pk': 1}), {
            "title": "new_titlenew_titlenew_titlenew_titlenew_titlenew_titlenew_titlenew_titlenew_titlenew_titlenew_titlenew_title",
            "summary": "new_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summary",
            "author": 3,
            "genre": "Rasskaz",
            "language": "ITA",
            "price": 100000000000000000000000000000,
            "count": 300000000000000000000000000000
            })
        self.assertFormError(resp, "form", "title", 'Слишком длинное название')
        self.assertFormError(resp, "form", "summary", 'Слишком длинное описание')
        self.assertFormError(resp, "form", "price", 'Слишком большое число')
        self.assertFormError(resp, "form", "count", 'Слишком большое число')

@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TestBookAddView(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username='user1', 
            password='1q2w3e4C'
            )
        user.save()  
        
        worker = User.objects.create_user(
            username='worker1', 
            password='1q2w3e4C'
            )
        worker.save()
        worker.user_permissions.add(Permission.objects.get(codename='add_book'))

        for num in range(6):
            Author.objects.create(
                surname="surname{0}".format(num),
                name="name{0}".format(num)
            )

    def test_bookadd_view_get_right(self):
        self.client.login(username='worker1', password='1q2w3e4C')
        resp1 = self.client.get('/book/add')
        resp2 = self.client.get(reverse("book_add"))
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp2.status_code, 200)
        self.assertTemplateUsed(resp1, "book_add.html")

    def test_bookadd_view_get_wrong(self):
        self.client.login(username='user1', password='1q2w3e4C')
        resp = self.client.get('/book/add')
        self.assertEqual(resp.status_code, 403)

    def test_bookadd_view_post(self):
        self.client.login(username='worker1', password='1q2w3e4C')
        resp = self.client.post(reverse('book_add'), {
            "title": "new_title",
            "image": create_image("test_image.jpg"),
            "summary": "new_summary",
            "author": 3,
            "genre": "Rasskaz",
            "language": "ITA",
            "price": 1000000,
            "count": 500
            })
        self.assertRedirects(resp, reverse('book_info', kwargs={'pk': 1}))
        book=Book.objects.get(id=1)
        author=Author.objects.get(id=3)
        self.assertEqual(book.title, "new_title")
        self.assertEqual(book.image, "media/test_image.jpg")
        self.assertEqual(book.summary, "new_summary")
        self.assertEqual(book.author, author)
        self.assertEqual(book.genre, "Rasskaz")
        self.assertEqual(book.language, "ITA")
        self.assertEqual(book.price, 1000000)
        self.assertEqual(book.count, 500)

    def test_bookadd_view_post_required(self):
        self.client.login(username='worker1', password='1q2w3e4C')
        resp = self.client.post(reverse('book_add'), {})
        self.assertFormError(resp, "form", "title", 'Поле обязательно для заполнения')
        self.assertFormError(resp, "form", "author", 'Поле обязательно для заполнения')
        self.assertFormError(resp, "form", "genre", 'Поле обязательно для заполнения')
        self.assertFormError(resp, "form", "language", 'Поле обязательно для заполнения')
        self.assertFormError(resp, "form", "price", 'Поле обязательно для заполнения')
        self.assertFormError(resp, "form", "count", 'Поле обязательно для заполнения')

    def test_bookadd_view_post_minvalue(self):
        self.client.login(username='worker1', password='1q2w3e4C')
        resp = self.client.post(reverse('book_add'), {
            "title": "new_title",
            "summary": "new_summary",
            "author": 3,
            "genre": "Rasskaz",
            "language": "ITA",
            "price": -1000000,
            "count": -500
            })
        self.assertFormError(resp, "form", "price", 'Некорректное значение')
        self.assertFormError(resp, "form", "count", 'Некорректное значение')

    def test_bookadd_view_post_maxvalue(self):
        self.client.login(username='worker1', password='1q2w3e4C')
        resp = self.client.post(reverse('book_add'), {
            "title": "new_titlenew_titlenew_titlenew_titlenew_titlenew_titlenew_titlenew_titlenew_titlenew_titlenew_titlenew_title",
            "summary": "new_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summarynew_summary",
            "author": 3,
            "genre": "Rasskaz",
            "language": "ITA",
            "price": 100000000000000000000000000000,
            "count": 300000000000000000000000000000
            })
        self.assertFormError(resp, "form", "title", 'Слишком длинное название')
        self.assertFormError(resp, "form", "summary", 'Слишком длинное описание')
        self.assertFormError(resp, "form", "price", 'Слишком большое число')
        self.assertFormError(resp, "form", "count", 'Слишком большое число')

class TestAuthorAddView(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username='user1', 
            password='1q2w3e4C'
            )
        user.save()  
        
        worker = User.objects.create_user(
            username='worker1', 
            password='1q2w3e4C'
            )
        worker.save()
        worker.user_permissions.add(Permission.objects.get(codename='add_author'))

    def test_authoradd_view_get_right(self):
        self.client.login(username='worker1', password='1q2w3e4C')
        resp1 = self.client.get('/author/add')
        resp2 = self.client.get(reverse("author_add"))
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp2.status_code, 200)
        self.assertTemplateUsed(resp1, "author_add.html")

    def test_authoradd_view_get_wrong(self):
        self.client.login(username='user1', password='1q2w3e4C')
        resp = self.client.get('/author/add')
        self.assertEqual(resp.status_code, 403)

    def test_authoradd_view_post(self):
        self.client.login(username='worker1', password='1q2w3e4C')
        resp = self.client.post(reverse('author_add'), {
            "surname": "new_surname",
            "name": "new_name",
            "patronymic": "new_patronymic",
            "date_of_birth": "1900-01-01",
            "date_of_death": "2000-12-12",
            })
        self.assertRedirects(resp, reverse('worker'))
        author=Author.objects.get(id=1)
        self.assertEqual(author.surname, "new_surname")
        self.assertEqual(author.name, "new_name")
        self.assertEqual(author.patronymic, "new_patronymic")
        self.assertEqual(str(author.date_of_birth), "1900-01-01")
        self.assertEqual(str(author.date_of_death), "2000-12-12")

    def test_authoradd_view_post_required(self):
        self.client.login(username='worker1', password='1q2w3e4C')
        resp = self.client.post(reverse('author_add'), {})
        self.assertFormError(resp, "form", "surname", 'Поле обязательно для заполнения')
        self.assertFormError(resp, "form", "name", 'Поле обязательно для заполнения')

    def test_authoradd_view_post_maxlength(self):
        self.client.login(username='worker1', password='1q2w3e4C')
        resp = self.client.post(reverse('author_add'), {
            "surname": "new_surnamenew_surnamenew_surnamenew_surnamenew_surnamenew_surnamenew_surnamenew_surnamenew_surnamenew_surnamenew_surname",
            "name": "new_namenew_namenew_namenew_namenew_namenew_namenew_namenew_namenew_namenew_namenew_namenew_namenew_namenew_namenew_namenew_namenew_name",
            "patronymic": "new_patronymicnew_patronymicnew_patronymicnew_patronymicnew_patronymicnew_patronymicnew_patronymicnew_patronymicnew_patronymicnew_patronymic",
            })
        self.assertFormError(resp, "form", "surname", 'Слишком длинная фамилия')
        self.assertFormError(resp, "form", "name", 'Слишком длинное имя')
        self.assertFormError(resp, "form", "patronymic", 'Слишком длинное отчество')

    def test_authoradd_view_post(self):
        self.client.login(username='worker1', password='1q2w3e4C')
        resp = self.client.post(reverse('author_add'), {
            "surname": "new_surname",
            "name": "new_name",
            "patronymic": "new_patronymic",
            "date_of_birth": "1900-01-01",
            "date_of_death": "1800-12-12",
            })
        self.assertEqual(resp.context["form"].errors["__all__"], ["Дата смерти не может быть раньше даты рождения"])

class TestLoginUser(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username='user1', 
            password='1q2w3e4C'
            )
        user.save()

    def test_loginuser_view_get(self):
        resp1 = self.client.get('/login/')
        resp2 = self.client.get(reverse("login"))
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp2.status_code, 200)
        self.assertTemplateUsed(resp1, "login.html")

    def test_loginuser_view_post_correct(self):
        resp = self.client.post(reverse('login'), {
            "username": "user1",
            "password": "1q2w3e4C",
            })
        self.assertRedirects(resp, reverse('index'))

    def test_loginuser_view_post_incorrect(self):  
        resp1 = self.client.post(reverse('login'), {
            "username": "user2",
            "password": "1q2w3e4C",
            })
        resp2 = self.client.post(reverse('login'), {
            "username": "user1",
            "password": "1q2w3e4CCCC",
            })
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp2.status_code, 200)

class TestRegisterUser(TestCase):
    @classmethod
    def setUpTestData(cls):
        Group.objects.create(name='clients')

    def test_registeruser_view_get(self):
        resp1 = self.client.get('/register/')
        resp2 = self.client.get(reverse("register"))
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp2.status_code, 200)
        self.assertTemplateUsed(resp1, "register.html")
    
    def test_registeruser_view_post_correct(self):
        resp = self.client.post(reverse('register'), {
            "username": "user1",
            "password1": "1q2w3e4C",
            "password2": "1q2w3e4C",
            "first_name": "Ivan",
            "last_name": "Smirnov",
            "email": "test@mail.ru",
            })
        self.assertRedirects(resp, reverse('index'))
        user=User.objects.get(id=1)
        self.assertEqual(user.username, "user1")
        self.assertEqual(user.first_name, "Ivan")
        self.assertEqual(user.last_name, "Smirnov")
        self.assertEqual(user.email, "test@mail.ru")

    def test_registeruser_view_post_incorrect(self):
        user=User.objects.create_user(
            username='user1', 
            password='1q2w3e4C',
            email='test@mail.ru'
            )
        user.save()
        resp1 = self.client.post(reverse('register'), {
            "username": "user1",
            "password1": "1q2w3e4C",
            "password2": "1q2w3e4C",
            "email": "testyy@mail.ru",
            })
        self.assertEqual(resp1.status_code, 200)
        resp2 = self.client.post(reverse('register'), {
            "username": "user2",
            "password1": "1q2w3e4C",
            "password2": "1q2w3e4CCC",
            "email": "testyy@mail.ru",
            })
        self.assertEqual(resp2.status_code, 200)
        resp3 = self.client.post(reverse('register'), {
            "username": "user2",
            "password1": "1q2w3e4C",
            "password2": "1q2w3e4C",
            "email": "test@mail.ru",
            })
        self.assertEqual(resp3.status_code, 200)

class TestPasswordChange(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username='user1', 
            password='1q2w3e4C'
            )
        user.save()

    def test_passwordchange_view_get_right(self):
        self.client.login(username='user1', password='1q2w3e4C')
        resp1 = self.client.get('/password_change/')
        resp2 = self.client.get(reverse("password_change"))
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp2.status_code, 200)
        self.assertTemplateUsed(resp1, "password_change.html")

    def test_passwordchange_view_get_wrong(self):
        resp = self.client.get(reverse("password_change"))
        self.assertEqual(resp.status_code, 403)

    def test_passwordchange_view_post_correct(self):
        self.client.login(username='user1', password='1q2w3e4C')
        resp = self.client.post(reverse("password_change"), {
            "old_password": "1q2w3e4C",
            "new_password1": "1qaz2wsxQ",
            "new_password2": "1qaz2wsxQ",
        })
        self.assertRedirects(resp, reverse('password_change'))
        login=self.client.login(username='user1', password='1qaz2wsxQ')
        self.assertTrue(login)

    def test_passwordchange_view_post_incorrect(self):
        self.client.login(username='user1', password='1q2w3e4C')
        resp1 = self.client.post(reverse("password_change"), {
            "old_password": "1q2w3e4CCC",
            "new_password1": "1qaz2wsxQ",
            "new_password2": "1qaz2wsxQ",
        })
        self.assertEqual(resp1.status_code, 200)
        resp2 = self.client.post(reverse("password_change"), {
            "old_password": "1q2w3e4C",
            "new_password1": "1qaz2wsxQ",
            "new_password2": "1qaz2wsxQQQQ",
        })
        self.assertEqual(resp2.status_code, 200)

class TestUpdateUser(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username='user1', 
            password='1q2w3e4C',
            first_name="Ivan",
            last_name="Smirnov",
            email="test@mail.ru",
            )
        user.save()

        user_test = User.objects.create_user(
            username='user2', 
            password='1q2w3e4C',
            email="tester@mail.ru",
            )
        user_test.save()

    def test_updateuser_view_get_right(self):
        self.client.login(username='user1', password='1q2w3e4C')
        resp1 = self.client.get('/user_update/')
        resp2 = self.client.get(reverse("user_update"))
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp2.status_code, 200)
        self.assertTemplateUsed(resp1, "user_update.html")
        self.assertEqual(resp1.context['form'].initial["first_name"], "Ivan")
        self.assertEqual(resp1.context['form'].initial["last_name"], "Smirnov")
        self.assertEqual(resp1.context['form'].initial["email"], "test@mail.ru")

    def test_updateuser_view_get_wrong(self):
        resp = self.client.get(reverse("user_update"))
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith('/login/'))

    def test_updateuser_view_post_correct(self):
        self.client.login(username='user1', password='1q2w3e4C')
        resp = self.client.post(reverse("user_update"), {
            "first_name": "Petr",
            "last_name": "Ivanov",
            "email": "testik@mail.ru"
        })
        messages=list(resp.context["messages"])
        self.assertEqual(str(messages[0]), "Профиль изменен")
        user=User.objects.get(username="user1")
        self.assertEqual(user.first_name, "Petr")
        self.assertEqual(user.last_name, "Ivanov")
        self.assertEqual(user.email, "testik@mail.ru")

    def test_updateuser_view_post_incorrect(self):
        self.client.login(username='user1', password='1q2w3e4C')
        resp1 = self.client.post(reverse("user_update"), {
            "first_name": "PetrPetrPetrPetrPetrPetrPetrPetrPetr",
            "last_name": "Ivanov",
            "email": "testik@mail.ru"
        })
        messages1=list(resp1.context["messages"])
        self.assertEqual(str(messages1[0]), "Ошибка редкатирования")

        resp2 = self.client.post(reverse("user_update"), {
            "first_name": "Petr",
            "last_name": "IvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanovIvanov",
            "email": "testik@mail.ru"
        })
        messages2=list(resp2.context["messages"])
        self.assertEqual(str(messages2[0]), "Ошибка редкатирования")

        resp3 = self.client.post(reverse("user_update"), {
            "first_name": "Petr",
            "last_name": "Ivanov",
            "email": "tester@mail.ru"
        })
        messages3=list(resp3.context["messages"])
        self.assertEqual(str(messages3[0]), "Ошибка редкатирования")

        resp4 = self.client.post(reverse("user_update"), {
            "first_name": "Petr",
            "last_name": "Ivanov",
            "email": "test.ru"
        })
        messages4=list(resp4.context["messages"])
        self.assertEqual(str(messages4[0]), "Ошибка редкатирования")

class TestLogout(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username='user1', 
            password='1q2w3e4C',
            )
        user.save()

    def test_logout_view(self):
        self.client.login(username='user1', password='1q2w3e4C')
        resp1 = self.client.get('/logout/')
        resp2 = self.client.get(reverse("logout"))
        self.assertEqual(resp1.status_code, 302)
        self.assertEqual(resp2.status_code, 302)
        self.assertTrue(resp1.url.startswith(''))
        self.assertTrue(resp2.url.startswith(reverse("index")))
        resp3=self.client.get(reverse("logout"))
        self.assertEqual(resp3.status_code, 302)
        self.assertTrue(resp3.url.startswith('/login/'))

class TestProfile(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username='user1', 
            password='1q2w3e4C',
            first_name="Ivan",
            last_name="Smirnov",
            email="test@mail.ru",
            )
        user.save()

        for num in range(6):
                Author.objects.create(
                    surname="surname{0}".format(num+1),
                    name="name{0}".format(num+1)
                )

        for num in range(5):
            Book.objects.create(
                title="title{0}".format(num+1),
                author=Author.objects.get(id=num+1),
                genre=Book.GENR_CORT[num+1][0],
                language=Book.LANG_CORT[num+1][0],
            )

        Buy.objects.create(
            user=User.objects.get(id=1),
            book=Book.objects.get(id=1)
        )

        Rent.objects.create(
            user=User.objects.get(id=1),
            book=Book.objects.get(id=1)
        )

        UserMoney.objects.create(
            user=User.objects.get(id=1),
            money=500
        )

    def test_profile_get(self):
        self.client.login(username='user1', password='1q2w3e4C')
        buys=Buy.objects.filter(user__username="user1")
        rents=Rent.objects.filter(user__username="user1")
        money=UserMoney.objects.filter(user__username="user1")
        resp1 = self.client.get('/profile/')
        resp2 = self.client.get(reverse("profile"))
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp2.status_code, 200)
        self.assertTemplateUsed(resp1, "profile.html")
        self.assertQuerysetEqual(resp1.context['buys'], buys)
        self.assertQuerysetEqual(resp1.context['rents'], rents)
        self.assertIn(resp1.context['money'], money)

    def test_profile_get_wrong(self):
        resp = self.client.get('/profile/')
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith('/login/'))

class TestWorker(TestCase):
    @classmethod
    def setUpTestData(cls):
        worker = User.objects.create_user(
            username='worker1', 
            password='1q2w3e4C',
            )
        worker.save()
        worker.user_permissions.add(Permission.objects.get(codename='add_book'))

        user = User.objects.create_user(
            username='user1', 
            password='1q2w3e4C',
            )
        user.save()

        Author.objects.create(
            surname="surname",
            name="name"
        )

        for num in range(15):
            Book.objects.create(
                title="title{0}".format(num+1),
                author=Author.objects.get(id=1),
                genre=Book.GENR_CORT[1][0],
                language=Book.LANG_CORT[1][0],
            )

    def test_worker_get(self):
        self.client.login(username='worker1', password='1q2w3e4C')
        books=Book.objects.all()
        resp1 = self.client.get('/worker/')
        resp2 = self.client.get(reverse("worker"))
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp2.status_code, 200)
        self.assertTemplateUsed(resp1, "worker.html")
        resp=self.client.get(reverse("worker")+'?page=1')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context["books"]), 10)
        self.assertQuerysetEqual(resp.context['books'], books[:10])

    def test_worker_get_wrong(self):
        resp1=self.client.get(reverse("worker"))
        self.assertEqual(resp1.status_code, 302)
        self.assertTrue(resp1.url.startswith('/login/'))
        self.client.login(username='user1', password='1q2w3e4C')
        resp2=self.client.get(reverse("worker"))
        self.assertEqual(resp2.status_code, 403)

class TestBuyBook(TestCase):
    @classmethod
    def setUpTestData(cls):
        user1 = User.objects.create_user(
            username='user1', 
            password='1q2w3e4C',
            )
        user1.save()
        user1.user_permissions.add(Permission.objects.get(codename='add_buy'))

        user2 = User.objects.create_user(
            username='user2', 
            password='1q2w3e4C',
            )
        user2.save()

        Author.objects.create(
            surname="surname",
            name="name"
        )

        Book.objects.create(
            title="title1",
            author=Author.objects.get(id=1),
            genre=Book.GENR_CORT[1][0],
            language=Book.LANG_CORT[1][0],
            price=100,
            count=10
        )

        UserMoney.objects.create(
            user=User.objects.get(id=1),
            money=150
        )

    def test_buybook_post(self):
        self.client.login(username='user1', password='1q2w3e4C')
        resp=self.client.post("/buybook/1")
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith('/profile/'))
        self.assertTrue(Buy.objects.filter(user__username="user1").filter(book__title="title1").exists())
        self.assertEqual(Book.objects.get(id=1).count, 9)
        self.assertEqual(UserMoney.objects.get(user__username="user1").money, 50)
        resp2=self.client.post(reverse("buybook", kwargs={'pk': 1}))
        self.assertEqual(resp2.status_code, 302)
        self.assertTrue(resp2.url.startswith(reverse('money_plus', args=["Недостаточно средств!"])))

    def test_buybook_post_wrong(self):
        resp1=self.client.post("/buybook/1")
        self.assertEqual(resp1.status_code, 302)
        self.assertTrue(resp1.url.startswith('/login/'))
        self.client.login(username='user2', password='1q2w3e4C')
        resp2=self.client.post(reverse("buybook", kwargs={'pk': 1}))
        self.assertEqual(resp2.status_code, 403)

class TestRentBook(TestCase):
    @classmethod
    def setUpTestData(cls):
        user1 = User.objects.create_user(
            username='user1', 
            password='1q2w3e4C',
            )
        user1.save()
        user1.user_permissions.add(Permission.objects.get(codename='add_rent'))

        user2 = User.objects.create_user(
            username='user2', 
            password='1q2w3e4C',
            )
        user2.save()

        Author.objects.create(
            surname="surname",
            name="name"
        )

        Book.objects.create(
            title="title1",
            author=Author.objects.get(id=1),
            genre=Book.GENR_CORT[1][0],
            language=Book.LANG_CORT[1][0],
            count=10
        )

    def test_rentbook_post(self):
        self.client.login(username='user1', password='1q2w3e4C')
        resp=self.client.post("/rentbook/1")
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith('/profile/'))
        self.assertTrue(Rent.objects.filter(user__username="user1").filter(book__title="title1").exists())
        self.assertEqual(Book.objects.get(id=1).count, 9)
        
    def test_rentbook_post_wrong(self):
        resp1=self.client.post("/rentbook/1")
        self.assertEqual(resp1.status_code, 302)
        self.assertTrue(resp1.url.startswith('/login/'))
        self.client.login(username='user2', password='1q2w3e4C')
        resp2=self.client.post(reverse("rentbook", kwargs={'pk': 1}))
        self.assertEqual(resp2.status_code, 403)

class TestBookDelete(TestCase):
    @classmethod
    def setUpTestData(cls):
        worker = User.objects.create_user(
            username='worker1', 
            password='1q2w3e4C',
            )
        worker.save()
        worker.user_permissions.add(Permission.objects.get(codename='delete_book'))

        user = User.objects.create_user(
            username='user1', 
            password='1q2w3e4C',
            )
        user.save()

        Author.objects.create(
            surname="surname",
            name="name"
        )

        for num in range(3):
            Book.objects.create(
                title="title{0}".format(num+1),
                author=Author.objects.get(id=1),
                genre=Book.GENR_CORT[1][0],
                language=Book.LANG_CORT[1][0],
            )
    
    def test_bookdelete_post(self):
        self.client.login(username='worker1', password='1q2w3e4C')
        self.assertTrue(Book.objects.filter(id=1).exists())
        resp=self.client.post("/bookdelete/1")
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith('/worker/'))
        self.assertFalse(Book.objects.filter(id=1).exists())

    def test_bookdelete_post_wrong(self):
        resp1=self.client.post("/bookdelete/1")
        self.assertEqual(resp1.status_code, 302)
        self.assertTrue(resp1.url.startswith('/login/'))
        self.client.login(username='user1', password='1q2w3e4C')
        resp2=self.client.post(reverse("book_delete", kwargs={'pk': 1}))
        self.assertEqual(resp2.status_code, 403)
        
class TestBuyDelete(TestCase):
    @classmethod
    def setUpTestData(cls):
        user1 = User.objects.create_user(
            username='user1', 
            password='1q2w3e4C',
            )
        user1.save()
        user1.user_permissions.add(Permission.objects.get(codename='delete_buy'))

        user2 = User.objects.create_user(
            username='user2', 
            password='1q2w3e4C',
            )
        user2.save()

        Author.objects.create(
            surname="surname",
            name="name"
        )

        for num in range(5):
            Book.objects.create(
                title="title{0}".format(num+1),
                author=Author.objects.get(id=1),
                genre=Book.GENR_CORT[1][0],
                language=Book.LANG_CORT[1][0],
            )

        for num in range(3):
            Buy.objects.create(
                user=User.objects.get(id=1),
                book=Book.objects.get(id=num+1)
            )
    
    def test_buydelete_post(self):
        self.client.login(username='user1', password='1q2w3e4C')
        self.assertTrue(Buy.objects.filter(user__username="user1").filter(book__id=1).exists())
        resp=self.client.post("/buydelete/1")
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith('/profile/'))
        self.assertFalse(Buy.objects.filter(user__username="user1").filter(book__id=1).exists())

    def test_buydelete_post_wrong(self):
        resp1=self.client.post("/buydelete/1")
        self.assertEqual(resp1.status_code, 302)
        self.assertTrue(resp1.url.startswith('/login/'))
        self.client.login(username='user2', password='1q2w3e4C')
        resp2=self.client.post(reverse("buydelete", kwargs={'pk': 1}))
        self.assertEqual(resp2.status_code, 403)

class TestBookReturn(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username='user1', 
            password='1q2w3e4C',
            )
        user.save()

        Author.objects.create(
            surname="surname",
            name="name"
        )

        for num in range(5):
            Book.objects.create(
                title="title{0}".format(num+1),
                author=Author.objects.get(id=1),
                genre=Book.GENR_CORT[1][0],
                language=Book.LANG_CORT[1][0],
                count=10,
            )

        for num in range(3):
            Rent.objects.create(
                user=User.objects.get(id=1),
                book=Book.objects.get(id=num+1)
            )

    def test_bookreturn_post(self):
        self.client.login(username='user1', password='1q2w3e4C')
        self.assertTrue(Rent.objects.filter(user__username="user1").filter(book__id=1).exists())
        resp=self.client.post("/bookreturn/1")
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith('/profile/'))
        self.assertFalse(Rent.objects.filter(user__username="user1").filter(book__id=1).exists())
        self.assertEqual(Book.objects.get(id=1).count, 11)

    def test_bookreturn_post_wrong(self):
        resp1=self.client.post("/bookreturn/1")
        self.assertEqual(resp1.status_code, 302)
        self.assertTrue(resp1.url.startswith('/login/'))

class TestDuty(TestCase):
    @classmethod
    def setUpTestData(cls):
        worker = User.objects.create_user(
            username='worker1', 
            password='1q2w3e4C',
            )
        worker.save()
        worker.user_permissions.add(Permission.objects.get(codename='add_book'))

        user1 = User.objects.create_user(
            username='user1', 
            password='1q2w3e4C',
            )
        user1.save()

        user2 = User.objects.create_user(
            username='user2', 
            password='1q2w3e4C',
            )
        user2.save()

        Author.objects.create(
            surname="surname",
            name="name"
        )

        for num in range(10):
            Book.objects.create(
                title="title{0}".format(num+1),
                author=Author.objects.get(id=1),
                genre=Book.GENR_CORT[1][0],
                language=Book.LANG_CORT[1][0],
                count=10,
            )

        for num in range(3):
            Rent.objects.create(
                user=User.objects.get(id=2),
                book=Book.objects.get(id=num+1)
            )
            Rent.objects.create(
                user=User.objects.get(id=3),
                book=Book.objects.get(id=num+5)
            )
    
    def test_bookreturn_get(self):
        self.client.login(username='worker1', password='1q2w3e4C')
        resp1=self.client.get("/duty/")
        self.assertEqual(resp1.status_code, 200)
        resp2=self.client.get(reverse("duty_list"))
        self.assertEqual(resp2.status_code, 200)
        self.assertTemplateUsed(resp1, "duty_list.html")
        self.assertQuerysetEqual(Rent.objects.filter(user__username="user1"), resp1.context["dictionary"]["user1"], ordered=False)
        self.assertQuerysetEqual(Rent.objects.filter(user__username="user2"), resp1.context["dictionary"]["user2"], ordered=False)

    def test_bookreturn_get_wrong(self):
        resp1=self.client.get("/duty/")
        self.assertEqual(resp1.status_code, 302)
        self.assertTrue(resp1.url.startswith('/login/'))
        self.client.login(username='user1', password='1q2w3e4C')
        resp2=self.client.get(reverse("duty_list"))
        self.assertEqual(resp2.status_code, 403)

class TestEmail(TestCase):
    @classmethod
    def setUpTestData(cls):
        worker = User.objects.create_user(
            username='worker1', 
            password='1q2w3e4C',
            email='worker1@mail.ru'
            )
        worker.save()
        worker.user_permissions.add(Permission.objects.get(codename='add_book'))

        user1 = User.objects.create_user(
            username='user1', 
            password='1q2w3e4C',
            email='user1@mail.ru'
            )
        user1.save()

        user2 = User.objects.create_user(
            username='user2', 
            password='1q2w3e4C',
            email='user2@mail.ru'
            )
        user2.save()

    def test_email_get(self):
        self.client.login(username='worker1', password='1q2w3e4C')
        resp1=self.client.get("/email/")
        self.assertEqual(resp1.status_code, 200)
        resp2=self.client.get(reverse("email"))
        self.assertEqual(resp2.status_code, 200)
        self.assertTemplateUsed(resp1, "email.html")

    def test_email_get_wrong(self):
        resp1=self.client.get("/email/")
        self.assertEqual(resp1.status_code, 302)
        self.assertTrue(resp1.url.startswith('/login/'))
        self.client.login(username='user1', password='1q2w3e4C')
        resp2=self.client.get(reverse("email"))
        self.assertEqual(resp2.status_code, 403)

    def test_email_post_correct(self):
        self.client.login(username='worker1', password='1q2w3e4C')
        resp=self.client.post(reverse("email"), {
            "address": [2, 3],
            "subject": "test_subject",
            "message": "test_message"
        })
        self.assertEqual(resp.status_code, 200)
        messages=list(resp.context["messages"])
        self.assertEqual(str(messages[0]), "Сообщение отправлено!")

    def test_email_post_incorrect(self):
        self.client.login(username='worker1', password='1q2w3e4C')
        resp=self.client.post(reverse("email"), {
            "address": [2],
            "subject": "subject\nInjection Test",
            "message": "test_message"
        })
        self.assertEqual(resp.status_code, 200)
        messages=list(resp.context["messages"])
        self.assertEqual(str(messages[0]), "Ошибка ввода!")

    def test_email_post_errors(self):
        self.client.login(username='worker1', password='1q2w3e4C')
        resp=self.client.post(reverse("email"), {
            "subject": "subjectsubjectsubjectsubjectsubjectsubjectsubjectsubjectsubjectsubjectsubjectsubjectsubject",
            "message": "test_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_messagetest_message"
        })
        self.assertFormError(resp, "form", "address", 'Поле обязательно для заполнения')
        self.assertFormError(resp, "form", "subject", 'Слишком длинная тема')
        self.assertFormError(resp, "form", "message", 'Слишком большое сообщение')

class TestMoneyPlus(TestCase):
    @classmethod
    def setUpTestData(cls):
        user1 = User.objects.create_user(
            username='user1', 
            password='1q2w3e4C',
            )
        user1.save()
        user1.user_permissions.add(Permission.objects.get(codename='add_usermoney'))

        user2 = User.objects.create_user(
            username='user2', 
            password='1q2w3e4C',
            )
        user2.save()

        UserMoney.objects.create(
            user=User.objects.get(id=1),
            money=150
        )

    def test_moneyplus_get(self):
        self.client.login(username='user1', password='1q2w3e4C')
        resp1=self.client.get("/money_plus/")
        self.assertEqual(resp1.status_code, 200)
        resp2=self.client.get(reverse("money_plus"))
        self.assertEqual(resp2.status_code, 200)
        self.assertTemplateUsed(resp1, "money_plus.html")

    def test_moneyplus_get_wrong(self):
        resp1=self.client.get("/money_plus/")
        self.assertEqual(resp1.status_code, 302)
        self.assertTrue(resp1.url.startswith('/login/'))
        self.client.login(username='user2', password='1q2w3e4C')
        resp2=self.client.get(reverse("money_plus"))
        self.assertEqual(resp2.status_code, 403)

    def test_moneyplus_post(self):
        self.client.login(username='user1', password='1q2w3e4C')
        resp=self.client.post(reverse("money_plus"), {
            "plus": 100
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith('/profile/'))
        self.assertEqual(UserMoney.objects.get(id=1).money, 250)

    def test_moneyplus_post_errors(self):
        self.client.login(username='user1', password='1q2w3e4C')
        resp1=self.client.post(reverse("money_plus"), {
            "plus": -5000
        })
        self.assertFormError(resp1, "form", "plus", 'Некорректное значение')
        resp2=self.client.post(reverse("money_plus"), {
            "plus": 5147483647
        })
        self.assertFormError(resp2, "form", "plus", 'Слишком большое число')


    

    





        








        



    


        



        

        
        
        
    


    

    




        






