from django.shortcuts import render
from django.http import HttpResponse

def databasepage(request):
    return HttpResponse("database world")
