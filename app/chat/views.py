from django.shortcuts import render
from django.http import HttpResponse

def chatpage(request):
    return HttpResponse("chat world")

#for development below, remove before launch
def mock(request):
    return render(request, 'chat/index.html')
