from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.core import serializers
from django.http import HttpResponse

from .forms import WordbookForm
from .models import Wordbook
from login.models import User

# スクレイピング用
from bs4 import BeautifulSoup 
import requests
import re

weblio_url='https://ejje.weblio.jp/content/'

def vocabpage(request):
    if request.method == 'POST':
        form = WordbookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('vocabpage')
    else:
        form = WordbookForm()
    
    search_query = request.GET.get('search_query', '')
    wordbook_data = Wordbook.objects.filter(
        Q(word__icontains=search_query) | Q(meaning__icontains=search_query)
    ).order_by('word') 

    context = {'wordbook_data': wordbook_data, 'form': form}
    return render(request, 'vocab/vocab.html', context)

def add_word(request):
    if request.method == 'POST':
        form = WordbookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('vocabpage')
    else:
        form = WordbookForm()
    return render(request, 'vocab/add_word.html', {'form': form})

def edit_word(request, user_id_id, word):
    word = get_object_or_404(Wordbook, user_id_id=user_id_id, word=word)
    if request.method == 'POST':
        form = WordbookForm(request.POST, instance=word)
        if form.is_valid():
            form.save()
            return redirect('vocabpage')
    else:
        form = WordbookForm(instance=word)
    return render(request, 'vocab/edit_word.html', {'form': form, 'user_id_id': user_id_id, 'word': word})


def delete_word(request, user_id_id, word):
    word = get_object_or_404(Wordbook, user_id_id=user_id_id, word=word)
    if request.method == 'POST':
        word.delete()
        return redirect('vocabpage')
    return render(request, 'vocab/delete_word.html', {'word': word})


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
            "user_id": User.objects.all()[0], # TODO
            "word": word,
            "meaning": japanese,
            "pronunciation": pronunciation,
            "category": partofspeech,
            "context": example,
        }

# def vocabpage(request):
    
#     # Postで追加
#     if request.method == "POST":
#         form = WordForm(request.POST)

#         # データがフォームに一致するかチェック
#         if form.is_valid():
#             form.save()
#             return redirect('/vocab')

#     # 追加（検索）
#     elif request.GET.get('w') != None:
#         dic = search_word(request.GET['w'])
#         form = Wordbook(**dic)
        
#         form.save()
#         return redirect('/vocab')

#     # 編集
#     # TODO wordを編集する場合は元のデータを削除
#     elif request.GET.get('u') != None:
#         word = request.GET['u']
        
#         try:
#             obj = Wordbook.objects.get(user_id=User.objects.all()[0], word=word)
#             obj.context = "updated"
#             obj.save()
        
#         except Wordbook.DoesNotExist:
#             print("no such vocabulary")
#             return redirect('/vocab')

#     # 削除
#     elif request.GET.get('d') != None:
#         word = request.GET['d']

#         try:
#             obj = Wordbook.objects.get(user_id=User.objects.all()[0], word=word)
#             obj.delete()
        
#         except Wordbook.DoesNotExist:
#             print("no such vocabulary")
#             return redirect('/vocab')

#     elif request.GET.get('a') != None:
        
#         # 単語帳のフォームを組み込んだページをレンダリング
#         dic = search_word(request.GET['a'])
#         form = WordForm(dic)

#         return render(request, 'vocab/add_word.html', {'form': form})

#     posts = Wordbook.objects.all()
#     post_list = serializers.serialize('json', posts, indent=2)

#     return HttpResponse(post_list, content_type="application/json; charset=utf-8")
