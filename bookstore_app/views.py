from re import template
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from .models import Author, Genre, Language, Book, Buy, Rent, UserMoney
from .forms import GenreForm, AuthorForm, LoginForm, LanguageForm, RegisterForm, SearchForm, UserUpdateForm, EmailForm, MoneyPlusForm, PasswordForm
from django.views import generic
from django.contrib import auth, messages
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django import forms

# Create your views here.


def index(request):
    books=None
    result=True
    author_form=AuthorForm(request.POST or None)
    genre_form=GenreForm(request.POST or None)
    language_form=LanguageForm(request.POST or None)
    search_form=SearchForm(request.POST or None)
    message="Выберете книгу"
    
    if request.POST.get("butsearchauthor"):
        if author_form.is_valid() and genre_form.is_valid():
            name_author=author_form.cleaned_data["author_list"]
            name_genre=genre_form.cleaned_data["genre_list"]
            if name_author is not None and name_genre is not None:
                books=Book.objects.filter(author=name_author).filter(genre=name_genre)
            elif name_author is None:
                books=Book.objects.filter(genre=name_genre)
            elif name_genre is None:
                books=Book.objects.filter(author=name_author)
        if not books:
                result=False
        
    if request.POST.get("butsearchtitle"):
        if search_form.is_valid():
            search_title=search_form.cleaned_data["search_title"]
            if search_title == '':
                message="Уточните запрос"
            else:
                books=Book.objects.filter(title__icontains=search_title)
                if not books:
                    result=False
    
    if request.POST.get("butsearchlanguage"):
        if language_form.is_valid():
            language=language_form.cleaned_data["language_list"]
            books=Book.objects.filter(language__in=language)
            if not books:
                result=False

    if result==False:
        message="Книги не найдены"
    
    return render (request, "index.html", 
        context={
        "books": books,
        "author_form": author_form,
        "genre_form": genre_form,
        "language_form": language_form,
        "search_form": search_form,
        "message": message
        })


class BookInfo(generic.DetailView):
    model=Book
    template_name="book_info.html"


class BookEdit(generic.UpdateView):
    model=Book
    template_name="book_edit.html"
    form_class=forms.modelform_factory(
        model=Book,
        fields='__all__',
        error_messages={
            'title': {'required': 'Поле обязательно для заполнения'},
            'author': {'required': 'Поле обязательно для заполнения'},
            'genre': {'required': 'Поле обязательно для заполнения'},
            'language': {'required': 'Поле обязательно для заполнения'},
            'price': {'required': 'Поле обязательно для заполнения',
                    'min_value': 'Некорректное значение!'},
            'count': {'required': 'Поле обязательно для заполнения',
                'min_value': 'Некорректное значение!'},
        })

    def form_valid(self, form):
        instance=form.save()
        instance.save()
        return HttpResponseRedirect(reverse('book_info', kwargs={'pk': instance.id}))

    def form_invalid(self, form):
        return super().form_invalid(form)


class BookAdd(generic.CreateView):
    model=Book
    template_name="book_add.html"
    form_class=forms.modelform_factory(
        model=Book,
        fields='__all__',
        error_messages={
            'title': {'required': 'Поле обязательно для заполнения'},
            'author': {'required': 'Поле обязательно для заполнения'},
            'genre': {'required': 'Поле обязательно для заполнения'},
            'language': {'required': 'Поле обязательно для заполнения'},
            'price': {'required': 'Поле обязательно для заполнения',
                    'min_value': 'Некорректное значение!'},
            'count': {'required': 'Поле обязательно для заполнения',
                'min_value': 'Некорректное значение!'},
        })

    def form_valid(self, form):
        instance=form.save()
        instance.save()
        return HttpResponseRedirect(reverse('book_info', kwargs={'pk': instance.id}))
    
    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)

class LoginUser(LoginView):
    template_name="login.html"
    form_class=LoginForm
    
    def get_success_url(self):
        return reverse_lazy(index)

    def form_invalid(self, form):
        return super().form_invalid(form)


class RegisterUser(generic.CreateView):
    template_name="register.html"
    form_class=RegisterForm

    def form_valid(self, form):
        user=form.save()
        user.groups.add(Group.objects.get(name='clients'))
        auth.login(self.request, user)
        UserMoney.objects.create(user=self.request.user, money=0)
        return redirect("index")
    
    def form_invalid(self, form):
        return super().form_invalid(form)

class PasswordChange(PasswordChangeView):
    template_name="password_change.html"
    form_class=PasswordForm

    def form_valid(self, form):
        user=form.save()
        update_session_auth_hash(self.request, user)
        messages.success(self.request, "Пароль успешно изменен")
        return HttpResponseRedirect(reverse('password_change'))

    def form_invalid(self, form):
        return super().form_invalid(form)
        

@login_required(login_url='login')
def updateuser(request):
    user=request.user 
    form=UserUpdateForm(initial={
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email_address': user.email
        })
    
    if request.method=='POST':
        form=UserUpdateForm(request.POST)
        if form.is_valid():
            user.first_name=form.cleaned_data["first_name"]
            user.last_name=form.cleaned_data["last_name"]
            user.email=form.cleaned_data["email_address"]
            user.save()
            messages.success(request, 'Профиль изменен')
        else:
            messages.info(request, 'Ошибка редкатирования')
          
    return render (request, "user_update.html", 
        context={
        "form": form,
        })


@login_required(login_url='login')
def logoutuser(request):
    auth.logout(request)
    return redirect ("index")

@login_required(login_url='login')
def profileuser(request):
    buys=Buy.objects.filter(user=request.user)
    rents=Rent.objects.filter(user=request.user)
    money=UserMoney.objects.get(user=request.user)
    return render (request, "profile.html", 
        context={
        "buys": buys,
        "rents": rents,
        "money": money,
        })

@login_required(login_url='login')
def workeruser(request):
    book_list=Book.objects.all()
    paginator=Paginator(book_list, 10)
    page=request.GET.get('page')
    try:
        books=paginator.page(page)
    except PageNotAnInteger:
        books=paginator.page(1)
    except EmptyPage:
        books=paginator.page(paginator.num_pages)
    return render (request, "worker.html",
        context={  
        "books": books,
        })

@login_required(login_url='login')
def buybook(request):
    if request.method=='POST':
        book=Book.objects.get(id=request.POST["hidden_id"])
        buy=Buy.objects.create(user=request.user, book=book)
        money=UserMoney.objects.get(user=request.user)
        if money.money >= book.price:
            book.count-=1
            money.money-=book.price
            buy.save()
            book.save()
            money.save()
            return redirect ("profile")
        else:
            return redirect ("money_plus", message="Недостаточно средств!")

@login_required(login_url='login')
def rentbook(request):
    if request.method=='POST':
        book=Book.objects.get(id=request.POST["hidden_id"])
        rent=Rent.objects.create(user=request.user, book=book)
        book.count-=1
        rent.save()
        book.save()
        return redirect ("profile")

@login_required(login_url='login')
def bookedit(request):
    if request.method=='POST':
        book_id=request.POST["hidden_id"]
        return redirect('book_update', pk=book_id)

@login_required(login_url='login')
def bookdelete(request):
     if request.method=='POST':
        book_id=request.POST["hidden_id"]
        Book.objects.get(id=book_id).delete()
        return redirect ("worker")

@login_required(login_url='login')
def buydelete(request):
    if request.method=='POST':
        buy_id=request.POST["hidden_id"]
        Buy.objects.get(id=buy_id).delete()
        return redirect ("profile")

@login_required(login_url='login')
def bookreturn(request):
    if request.method=='POST':
        rent_id=request.POST["hidden_id"]
        rent=Rent.objects.get(id=rent_id)
        book=Book.objects.get(id=rent.book.id)
        book.count+=1
        rent.delete()
        book.save()
        return redirect ("profile")

@login_required(login_url='login')
def duty(request):
    dictionary={}
    user_list=Rent.objects.all().values('user', 'user__username').distinct()

    for u in user_list:
        books=Rent.objects.filter(user=u['user'])
        dictionary[u['user__username']]=books

    return render(request, "duty_list.html",
        context={  
        "dictionary": dictionary,
        })
        
@login_required(login_url='login')
def email(request):
    form=EmailForm(request.POST)
    if request.method=='POST':
        if form.is_valid():
            subject=form.cleaned_data["subject"]
            message=form.cleaned_data["message"]
            address=[]
            fromemail=request.user.email
            
            users=form.cleaned_data["address"]
            for user in users:
                address.append(user.email)
            
            try:
                send_mail(subject, message, 
                        fromemail,
                        address)
            except BadHeaderError:
                messages.success(request, 'Ошибка ввода!')
            messages.success(request, 'Сообщение отправлено!')    
    return render(request, "email.html", 
        context={
            "form": form,
        }
    )   

@login_required(login_url='login')
def money_plus(request, message=''):
    money=UserMoney.objects.get(user=request.user)
    form=MoneyPlusForm(request.POST)
    if request.method=='POST':
        if form.is_valid():
            plus=form.cleaned_data["plus"]
            money.money+=plus
            money.save()
    return render (request, "money_plus.html",
        context={  
        "money": money,
        "form": form,
        "message": message,
        })