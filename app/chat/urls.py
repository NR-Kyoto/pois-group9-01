from django.urls import path
from . import views

app_name = 'chat' #for namespacing of urls
urlpatterns = [
    path('', views.chatpage, name='chatpage'),


    #for development below, remove before launch
    path('mock/', views.mock, name='mock'),
]