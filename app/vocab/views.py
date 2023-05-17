from django.shortcuts import render, redirect
from django.core import serializers
from django.http import HttpResponse

from urllib.parse import urlencode

from .models import Wordbook
from .forms import WordForm
from login.models import User

from bs4 import BeautifulSoup # スクレイピング用
import requests
import re

weblio_url='https://ejje.weblio.jp/content/'

def vocabpage(request):
    
    if request.GET.get('w') != None:
        dic = search_word(request.GET['w'])
        dic['user_id'] = User.objects.all()[0]
        form = Wordbook(**dic)
        
        # データがフォームに一致するかチェック
        # if form.is_valid():
        form.save()
        return redirect('/vocab')

    posts = Wordbook.objects.all()
    post_list = serializers.serialize('json', posts)

    return HttpResponse(post_list, content_type="application/json; charset=utf-8")

# 単語追加
def add_word(request):

    # requestがPostならデータベースに追加
    if request.method == "POST":
        form = WordForm(request.POST)

        # データがフォームに一致するかチェック
        if form.is_valid():
            form.save()
            return redirect('/vocab')

    else:
        # 単語帳のフォームを組み込んだページをレンダリング
        form = WordForm()
        return render(request, 'vocab/add_word.html', {'form': form})

# 単語削除
def delete_word(request):

    try:
        word = Wordbook.objects.get(user_id=1, word='dog')
        word.delete()

        return redirect('/vocab')

    except Wordbook.DoesNotExist:
        print("404")
        return redirect('/vocab')

# 編集

# 英単語からの自動入力
# weblioをスクレイピング
def search_word(word):

    # weblioで検索
    response = requests.get(weblio_url+word)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 発音記号
    pronunciation = soup.find(class_='KejjeHt').get_text() if soup.find(class_='KejjeHt') else ''
    
    # 品詞
    partofspeech = soup.find(class_='KnenjSub', id='KnenjPartOfSpeechIndex0').get_text() if soup.find(class_='KnenjSub', id='KnenjPartOfSpeechIndex0') else ''

    # 日本語訳
    japanese = ''
    if soup.find(class_='lvlB'):
        tmp = soup.find(class_='lvlB').get_text()
        tmp1 = re.sub("《.*》", "", tmp)
        japanese = re.sub("[.]", "", tmp1)
    else:
        lev0 = soup.find_all(class_='level0')

        if len(lev0) != 0:
            tmp1 = re.sub("《.*》", "", lev0[1].get_text())
            japanese = re.sub("[.]", "", tmp1)

    # 例文
    example = soup.find(class_='KejjeYrEn').get_text() if soup.find(class_='KejjeYrEn') else ''

    return {
            "user_id": None,
            "word": word,
            "meaning": japanese,
            "pronunciation": pronunciation,
            "category": partofspeech,
            "pronunciation": example,
        }
        