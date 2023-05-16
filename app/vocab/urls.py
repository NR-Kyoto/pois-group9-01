from django.urls import path
from . import views

urlpatterns = [
    path('', views.vocabpage, name='vocabpage'),
    path('add', views.add_word, name='add'),
]