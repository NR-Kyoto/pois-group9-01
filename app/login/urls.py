from . import views
from django.urls import path

urlpatterns = [
    path('signup/', views.MySignupView.as_view(), name='signup'),
    path('', views.MyLoginView.as_view(), name='login'),
    path('logout/', views.MyLogoutView.as_view(), name='logout'),
]