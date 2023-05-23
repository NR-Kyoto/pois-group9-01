from django.urls import path
from . import views

urlpatterns = [
    path('', views.evaluationpage, name='evaluationpage'),
]

urlpatterns = [
    path('', views.user_profile, name='user_profile'),
]