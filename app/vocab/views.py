from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.core import serializers
from django.http import HttpResponse, JsonResponse

from .forms import WordbookForm
from .models import Wordbook
from login.models import User

# スクレイピング用
from bs4 import BeautifulSoup 
import requests
import re

from deep_translator import GoogleTranslator # 翻訳

weblio_url='https://ejje.weblio.jp/content/'

# TODO ユーザIDを認証データから取得

def vocabpage(request):

    form = WordbookForm()
    
    search_query = request.GET.get('search_query', '')

    # 検索にかかる単語を返す
    wordbook_data = Wordbook.objects.filter(
        Q(word__icontains=search_query) | Q(meaning__icontains=search_query)
    ).order_by('word') 

    context = {'wordbook_data': wordbook_data, 'form': form}

    return render(request, 'vocab/vocab.html', context)

def add_word(request):

    # Saveボタンが押されたら，追加して単語帳ページにリダイレクト
    if request.method == 'POST':
        form = WordbookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('vocabpage')
    else:
        form = WordbookForm()

    word = search_word()

    return render(request, 'vocab/add_word.html', {'form': form})

def edit_word(request, user_id_id, word):
#     # TODO wordを編集する場合は元のデータを削除

    # 該当データを取得
    word = get_object_or_404(Wordbook, user_id_id=user_id_id, word=word)

    # Saveボタンが押されたら，編集して単語帳ページにリダイレクト
    if request.method == 'POST':
        form = WordbookForm(request.POST, instance=word)
        if form.is_valid():
            form.save()
            return redirect('vocabpage')
    else:
        form = WordbookForm(instance=word)

    return render(request, 'vocab/edit_word.html', {'form': form, 'user_id_id': user_id_id, 'word': word})


def delete_word(request, user_id_id, word):

    # 該当データを取得
    word = get_object_or_404(Wordbook, user_id_id=user_id_id, word=word)

    # deleteボタンが押されたら，削除して単語帳ページにリダイレクト
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

    # 日本語訳
    japanese = ''
    if soup.find(class_='lvlB'):
        tmp = soup.find(class_='lvlB').get_text()
        tmp1 = re.sub("《.*》", "", tmp)
        japanese = re.sub("[.]", "", tmp1)
    elif soup.find(class_='level0'):
        lev0 = soup.find_all(class_='level0')

        if len(lev0) >= 2:
            tmp1 = re.sub("《.*》", "", lev0[1].get_text())
            japanese = re.sub("[.]", "", tmp1)

    # 検索できなかった場合は例外を発生
    else:
        raise ValueError('cannot find word!')

    # 発音記号
    pronunciation = soup.find(class_='KejjeHt').get_text() if soup.find(class_='KejjeHt') else ''
    
    # 品詞
    partofspeech = soup.find(class_='KnenjSub', id='KnenjPartOfSpeechIndex0').get_text() if soup.find(class_='KnenjSub', id='KnenjPartOfSpeechIndex0') else ''

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

# Chat中に選択された単語
def mock_post_selected(request):
    if request.method == 'POST':
        selected = json.loads(request.POST["selected"])
        text = selected["text"]
        context = selected["context"]

        res = {"text": text}

        # 単語かどうか
        w_flag = True

        # スクレイピングが成功した場合は単語
        try:
            data = search_word(text)
            res['meaning'] = data['meaning']
            res['category'] = data['category']

        # スクレイピングが失敗した場合は翻訳
        except ValueError:
            w_flag = False
            res['meaning'] = GoogleTranslator(source='auto',target='ja').translate(text)

        res['word_falg'] = w_flag
            
        print(res)

        return JsonResponse(res)

# Chat中の単語登録
# TODO error時の処理
def mock_add_word(request):

    res = {"saved" : False}
    if request.method == 'POST':
        selected = json.loads(request.POST.get("selected"))

        dic = search_word(selected["text"])
        dic['context'] = selected["context"]
        form = Wordbook(**dic)

        form.save()
        res['saved'] = True

    return JsonResponse(res)
