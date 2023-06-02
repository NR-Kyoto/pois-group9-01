from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

def homepage(request):
    return render(request, 'home/home.html', {'username': request.user.username})