from django.shortcuts import render
from django.http import HttpResponse

from vocab.models import Wordbook

def vocabpage(request):
    posts = Wordbook.objects.all()
    return HttpResponse(posts[0])