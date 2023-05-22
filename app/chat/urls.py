from django.urls import path
from . import views

app_name = 'chat' #for namespacing of urls
urlpatterns = [
    path('', views.chatpage, name='chatpage'),


    #for development below, remove before launch
    path('mock/', views.mock, name='mock'),
    path('mock_post/', views.mock_post, name='mock_post'),
    path('mock_post_audio/', views.mock_post_audio, name='mock_post_audio'),
    # next one should be in the vocab app
    path('mock_post_selected/', views.mock_post_selected, name='mock_post_selected'),


]