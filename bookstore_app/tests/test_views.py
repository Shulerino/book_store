from urllib import response
import django
from django.conf import settings
from django.test import TestCase, override_settings
from bookstore_app.models import *
from bookstore_app.forms import *
from unittest import mock
from django.core.files import File


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
import shutil
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TestBookDetailView(TestCase):
    @classmethod
    def setUpTestData(cls):
        # image_list=[]
        # for num in range(5):
        #     image=mock.MagicMock(spec=File)
        #     image.name="image{0}.jpg".format(num+1)
        #     image_list.append(image)
        
        for num in range(6):
            Author.objects.create(
                surname="surname{0}".format(num),
                name="name{0}".format(num)
            )

        for num in range(5):
            Book.objects.create(
                title="title{0}".format(num+1),
                #image=image_list[num],
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
        #self.assertEqual(book.image, resp1.context["book"].image)
        self.assertIn(book.summary, resp1.context["book"].summary)
        self.assertEqual(book.author, resp1.context["book"].author)
        self.assertIn(book.genre, resp1.context["book"].genre)
        self.assertIn(book.language, resp1.context["book"].language)
        self.assertEqual(book.price, resp1.context["book"].price)
        self.assertEqual(book.count, resp1.context["book"].count)
        print(book.image)
        print(resp1.context["book"].image)




        






