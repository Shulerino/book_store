from urllib import response
from django.test import TestCase
from bookstore_app.models import *
from bookstore_app.forms import *

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
                genre=Book.GENR_CORT[num+1],
                language=Book.LANG_CORT[num+1],
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
    
    # def test_index_genre(self):
    #     books=Book.objects.filter(genre=("Basnya", "Басня"))
    #     resp1 = self.client.post(reverse('index'), {
    #         "butsearchauthor": True,
    #         "genre_list": 'Basnya',
    #         })
    #     self.assertQuerysetEqual(resp1.context["books"], books)

class TestBookDetailView(TestCase):
    @classmethod
    def setUpTestData(cls):
        for num in range(6):
            Author.objects.create(
                surname="surname{0}".format(num),
                name="name{0}".format(num)
            )

        for num in range(5):
            Book.objects.create(
                title="title{0}".format(num+1),
                author=Author.objects.get(id=num+1),
                genre=Book.GENR_CORT[num+1],
                language=Book.LANG_CORT[num+1],
            )
    
    def test_bookdetail_view_get(self):
        resp1 = self.client.get('/book/1')
        resp2 = self.client.get('/book/105')
        resp3 = self.client.get(reverse("book_info", kwargs={'pk': 1}))
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp2.status_code, 404)
        self.assertEqual(resp3.status_code, 200)
        self.assertTemplateUsed(resp1, "book_info.html")


        






