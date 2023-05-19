from django.urls import path
from . import views

urlpatterns = [
    path('', views.vocabpage, name='vocabpage'),
    path('add/', views.add_word, name='add_word'),
    path('delete/<int:user_id_id>/<str:word>/', views.delete_word, name='delete_word'),
    path('edit/<int:user_id_id>/<str:word>/', views.edit_word, name='edit_word'),
]