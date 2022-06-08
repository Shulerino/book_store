from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('book/<int:pk>', views.BookInfo.as_view(), name='book_info'),
    path('book/<int:pk>/update', views.BookEdit.as_view(), name='book_update'),
    path('book/add', views.BookAdd.as_view(), name='book_add'),
    path('bookdelete/<int:pk>', views.bookdelete, name='book_delete'),
    path('user_update/', views.updateuser, name='user_update'),
    path('login/', views.LoginUser.as_view(), name='login'),
    path('register/', views.RegisterUser.as_view(), name='register'),
    path('password_change/', views.PasswordChange.as_view(), name='password_change'),
    path('logout/', views.logoutuser, name='logout'),
    path('profile/', views.profileuser, name='profile'),
    path('worker/', views.workeruser, name='worker'),
    path('buybook/<int:pk>', views.buybook, name='buybook'),
    path('rentbook/<int:pk>', views.rentbook, name='rentbook'),
    path('buydelete/<int:pk>', views.buydelete, name='buydelete'),
    path('bookreturn/<int:pk>', views.bookreturn, name='bookreturn'),
    path('duty/', views.duty, name='duty_list'),
    path('email/', views.email, name='email'),
    path('money_plus/', views.money_plus, name='money_plus'),
    path('money_plus/<str:message>/', views.money_plus, name='money_plus'),
] + static (settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)