from django.shortcuts import render
from django.http import HttpResponse

def vocabpage(request):
    return HttpResponse("vocabrary world")