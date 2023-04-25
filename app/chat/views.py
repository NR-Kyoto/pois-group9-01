from django.shortcuts import render
from django.http import HttpResponse

def chatpage(request):
    return HttpResponse("chat world")
