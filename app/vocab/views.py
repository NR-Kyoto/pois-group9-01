from django.shortcuts import render
from django.core import serializers
from django.http import HttpResponse

from vocab.models import Wordbook

def vocabpage(request):
    posts = Wordbook.objects.all()
    post_list = serializers.serialize('json', posts)
    return HttpResponse(post_list, content_type="text/json-comment-filtered; charset=utf-8")

