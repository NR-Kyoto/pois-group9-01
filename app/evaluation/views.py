from django.shortcuts import render
from django.http import HttpResponse

def evaluationpage(request):
    return HttpResponse("evaluation world")
