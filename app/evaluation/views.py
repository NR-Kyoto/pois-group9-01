from django.shortcuts import render, redirect 
from django.http import HttpResponse

from dataclasses import dataclass # 構造体
from deep_translator import GoogleTranslator # 翻訳
import language_tool_python # 文法チェック
import re # 正規表現
import json # ResponseをJsonで
import os
import collections
# import difflib
import base64, io, subprocess, tempfile

import azure.cognitiveservices.speech as speech_sdk

from chat.models import Audio

# 認証情報を外部ファイルから読み出す
COG_SERVICE_KEY=os.getenv('COG_SERVICE_KEY')
COG_SERVICE_REGION=os.getenv('COG_SERVICE_REGION')

check_categories = ['CONFUSED_WORDS', 'GRAMMAR', 'REPETITIONS', 'TYPOS']

@dataclass(init=False)
class error:

    index: int      # 対象文の番号
    sentence: str   # 元の文
    errtype: str    # ruleId
    start: int      # 文内での開始位置
    end: int        # 文内での終了位置
    message: str    # エラーメッセージ
    suggestion: str # 正しい文

    def __init__(self, index, match):
        self.index = index
        self.sentence = match.sentence
        self.errtype = match.ruleId
        self.start = match.offset
        self.end = self.start + match.errorLength
        # self.message = GoogleTranslator(source='auto',target='ja').translate(match.message)
        self.suggestion = match.sentence[:self.start] + match.replacements[0] + match.sentence[self.end:]

        # カッコ内の英単語がそのままになるようにメッセージを翻訳
        bra_pos = list(re.compile(r'\“.*?\”|\‘.*?\’').finditer(match.message))
        
        if len(bra_pos) == 0:
            self.message = GoogleTranslator(source='auto',target='ja').translate(match.message)
        else:
            # XXXで置き換え
            tmp_m = ""
            start = 0
            for i, pos in enumerate(bra_pos):
                tmp_m += match.message[start:pos.start()] + "\"XXX" + str(i) + "\""
                start = pos.end()
            tmp_m += match.message[start:]

            # 翻訳
            trans = GoogleTranslator(source='auto',target='ja').translate(tmp_m)

            # 元の単語に置き換える
            for i, pos in enumerate(bra_pos):
                trans = trans.replace("XXX" + str(i), match.message[pos.start()+1:pos.end()-1])
            
            # TODO 全部翻訳するのは時間がかかるので一部に変更
            self.message = trans

    def to_html(self):
        html = '<div>'
        html += '<p>' + self.sentence[:self.start]
        html += '<strong>' + self.sentence[self.start:self.end] + '</strong>'
        html += self.sentence[self.end:] + '</p>'
        html += '<p>' + self.message + '</p>'
        html += '<p>fixed : ' + self.suggestion + '</p>'
        html += '</div>'
        return html
    
    def to_json(self):
        dic = dict({
            "sentence" : self.sentence,
            "start_pos" : self.start,
            "end_pos" : self.end,
            "error_message" : self.message,
            "fixed_sentence" : self.suggestion
        })
    
        return dic
    
# 評価
# 文章なし -> 評価しない
# 文章あり，音声なし -> 文法のみ
def evaluationpage(request):

    #---- Chatからのデータの受けとりと音声評価 ----#

    # Chatページからデータを取得
    queryset = Audio.objects.order_by('id').values()

    # データがなければチャットページにリダイレクト
    if queryset.count() == 0:
        return redirect('/chat/mock')

    texts = [] # Chat-GPTに送ったテキスト
    
    # 音声の評価
    speech_scores = {
            "score": 0,
            "accuracy_score": 0,
            "fluency_score": 0,
	        "completeness_score": 0,
	        "words": []
        }

    for item in queryset:

        text = item["text"]
        if not text: continue
        texts.append(text)
        
        if item["fields"]["audio"] != None:

            # webm -> wav
            with tempfile.NamedTemporaryFile(delete=True, suffix="_webm") as audio_webm:
                audio_webm.write(base64.b64decode(item["fields"]["audio"]))

                with tempfile.NamedTemporaryFile(delete=True, suffix="_wav") as audio_wav:
                    command = ['ffmpeg', '-y', '-i', str(audio_webm.name),'-f', 'wav', '-c:a', 'pcm_s16le', str(audio_wav.name)]
                    
                    # 変換ができたかチェック
                    try:
                        subprocess.run(command, check=True)

                    except subprocess.CalledProcessError:
                        continue
                    
                    # 音声評価
                    try:
                        result = evaluate_speech(text, audio_wav.name)
                        
                    except ValueError:
                        continue

                    speech_scores['score'] += result['score']
                    speech_scores['accuracy_score'] += result['accuracy_score']
                    speech_scores['fluency_score'] += result['fluency_score']
                    speech_scores['completeness_score'] += result['completeness_score']
                    speech_scores['words'] += result['words']

    # 評価した内容をデータベースから削除
    Audio.objects.all().delete()

    # 単語ごとの発音評価でソート
    sorted_words = sorted(speech_scores['words'], key=lambda x: x['score'])
    

    #---- 文法評価 ----#

    # 文章がない場合はチャットページにリダイレクト
    if not texts:
        return redirect('/chat/mock')

    sentances = split_sentances(texts)
    errors = check_grammar(sentances)
    grammar_score = get_grammar_score(len(sentances), errors) # 文法のスコア　0~5点
    

    #---- 送信データ ----#
    data = {
        "total_score" : grammar_score + speech_scores['score'],
        "grammar" : {
            "score" : grammar_score,
            "weaks" : grammar_weak_ranking(errors)
        },
        "speech" : {
            "score" : speech_scores['score'],
            "weaks" : [sorted_words[i] for i in range(min(len(sorted_words), 5)) if sorted_words[i]['score'] != 5.0]
        }
    }

    return render(request, 'evaluation/evaluation.html', data)


# 1文ずつに分割
def split_sentances(texts):

    sentances = []
    for text in texts:
        splited = re.split('[.?!]', text)
        sentances += [s if s[0] != ' ' else s[1:] for s in splited]
        if '' in sentances: sentances.remove('')

    return sentances

# sentances : 発話した文のリスト
def check_grammar(sentances):

    tool = language_tool_python.LanguageTool('en-US')
    
    errors = []
    for i, s in enumerate(sentances):
        # 文法をチェック
        matches = tool.check(s)

        # 定められたカテゴリに合うものだけを記録
        errors += [error(i, match) for match in matches if (match.category in check_categories)]

    tool.close()

    return errors

# 文法のスコアを返す
# 文法的間違えのなかった文の数 / 全文数 * 5
def get_grammar_score(sentance_num, errors):
    err_setnace_num = len(set([e.index for e in errors]))
    return (sentance_num - err_setnace_num) / sentance_num * 5

# 重複して登場するエラーの種類をランキング
def grammar_weak_ranking(errors):
    etypes = [e.errtype for e in errors]
    c = collections.Counter(etypes)

    # 辞書（Json形式）にする
    dicl = []
    for p in c.most_common(3):
        dicl.append(dict({
                "type" : p[0],
                "count" : p[1],
                "examples" : [e.to_json() for e in errors if e.errtype == p[0]][:3] # 3個まで例を表示
            }))

    # 出現回数上位三つを表示
    return dicl


# 音声認識の評価
def evaluate_speech(script, path):

    # 評価パラメータ
    # 5段階評価，文・単語を評価
    pronunciation_config = speech_sdk.PronunciationAssessmentConfig(
        reference_text=script,
        grading_system=speech_sdk.PronunciationAssessmentGradingSystem.FivePoint,
        granularity=speech_sdk.PronunciationAssessmentGranularity.Word)

    # 諸設定
    speech_config = speech_sdk.SpeechConfig(COG_SERVICE_KEY, COG_SERVICE_REGION)
    audio_config = speech_sdk.AudioConfig(filename=path)
    speech_recognizer = speech_sdk.SpeechRecognizer(speech_config, audio_config)

    # 音声を評価
    pronunciation_config.apply_to(speech_recognizer)
    result = speech_recognizer.recognize_once()

    pronunciation_result = speech_sdk.PronunciationAssessmentResult(result)

    words = []
    try:
        for word in pronunciation_result.words:
            words.append({
                "word": word.word,
                "score": word.accuracy_score
            })

    # wordsがない＝音声の入っていないデータ
    except AttributeError:
        raise ValueError

    dic = dict({
            "score": pronunciation_result.pronunciation_score, # 総評的な点数
            "accuracy_score": pronunciation_result.accuracy_score, # 発音がどれだけ正しいのか
            "fluency_score": pronunciation_result.fluency_score, # 流暢さ（単語間隔など）
	        "completeness_score": pronunciation_result.completeness_score,  # 正解文章に対してどれだけちゃんと発音したか＝ぬけがないか
	        "words": words
        })

    return dic
