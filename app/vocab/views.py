from django.shortcuts import render, redirect
from django.core import serializers
from django.http import HttpResponse

from .models import Wordbook
from .forms import WordForm

def vocabpage(request):
    posts = Wordbook.objects.all()
    post_list = serializers.serialize('json', posts)
    return HttpResponse(post_list, content_type="text/json-comment-filtered; charset=utf-8")

# 単語追加
def add_word(request):

    # requestがPostならデータベースに追加
    if request.method == "POST":
        form = WordForm(request.POST)

        # データがフォームに一致するかチェック
        if form.is_valid():
            form.save()
            p = redirect('/vocab')
            print(p)
            return p

    else:
        # 単語帳のフォームを組み込んだページをレンダリング
        form = WordForm()
        return render(request, 'vocab/add_word.html', {'form': form})

# 単語削除

# 編集

