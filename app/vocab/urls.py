from django.urls import path
from . import views

urlpatterns = [
    path('', views.vocabpage, name='vocabpage'),
    path('add/', views.add_word, name='add_word'),
    path('autofill_add/', views.autofill_word, name='autofill_word'),
    path('delete/<str:word>/', views.delete_word, name='delete_word'),
    path('edit/<str:word>/', views.edit_word, name='edit_word'),
    
    # Chatページからの呼び出し・登録
    path('mock_post_selected/', views.mock_post_selected, name='mock_post_selected'),
    path('mock_add_word/', views.mock_add_word, name='mock_post_add'),
]