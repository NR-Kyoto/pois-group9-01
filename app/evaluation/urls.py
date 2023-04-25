from django.urls import path
from . import views

urlpatterns = [
    path('', views.evaluationpage, name='evaluationpage'),
]