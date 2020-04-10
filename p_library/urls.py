from django.contrib import admin  
from django.urls import path  

from . import views
  
app_name = 'p_library'  
urlpatterns = [  
    path('author/create', views.AuthorEdit.as_view(), name='author_create'),  
    path('authors', views.AuthorList.as_view(), name='authors_list'),
    path('author/create_many', views.author_create_many, name='author_create_many'),
    path('author_book/create_many', views.books_authors_create_many, name='author_book_create_many'),
    path('friend/create', views.FriendEdit.as_view(), name='friend_create'),  
    path('friends', views.FriendsList.as_view(), name='friends_list'),
    path("lended", views.lended),
    path("lend_return", views.lend_return),
    path("do_lend_return/", views.do_lend_return),        
]