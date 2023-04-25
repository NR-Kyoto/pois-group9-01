from django.shortcuts import render
from django.http import HttpResponse

def loginpage(request):
    return HttpResponse("login world")