from django.shortcuts import render
from django.http import HttpResponse

from dataclasses import dataclass # 構造体
from deep_translator import GoogleTranslator # 翻訳
import language_tool_python # 文法チェック

import re # 正規表現
import json # ResponseをJsonで
import collections
import difflib

from django.shortcuts import render
from django.http import HttpResponse

from django.shortcuts import render
from django.http import HttpResponse

import json
import azure.cognitiveservices.speech as speech_sdk

import os


check_categories = ['CONFUSED_WORDS', 'GRAMMAR', 'REPETITIONS', 'TYPOS']

texts = [
    "Hey, did you was at the party last night?",
    "No, I didn't went. I was study for my exam.",
    "Oh, that's right. I forgot about your exam. Did you did well?",
    "Yes, I think I did good. I answered all of the questions correctly.",
    "That's great! So, did you went home right after the exam?",
    "No, I went to the mall to buy some clothes. I falled in love with a jacket that I saw there.",
    "Ah, I see. Did you bought the jacket?",
    "Yes, I did. It was expensive, but it was worth it.",
    "Sounds like you had a busy day yesterday. I was stayed at home and watched TV all day.",
    "That sounds relaxing. What did you watched?",
    "I watched a movie called 'Jurassic Park'. It was very exciting.",
    "Oh, I have saw that movie before. I liked it too. Did you knew that they made a new one?",
    "No, I didn't knew that. Is it good?",
    "Yes, it's very good. You should go see it."
]

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
            self.message = trans

    
    def to_json(self):
        dic = dict({
            "sentence" : self.sentence,
            "start_pos" : self.start,
            "end_pos" : self.end,
            "error_message" : self.message,
            "fixed_sentence" : self.suggestion
        })
        return dic
    
def evaluationpage(request):

    sentances = split_sentances(texts)
    errors = check_grammar(sentances)

    # 文法のスコア　0~5点
    score = get_grammar_score(len(sentances), errors)

    # errors_json = []
    # for e in errors:

    #     # html += e.to_html()
    #     errors_json.append(e.to_json())

    # 音声の評価スコア
    result_json = evaluate_speech('What time is it now in Japan ?')
    pronunciation_score = result_json["score"]

    # total_scoreの計算
    total_score = score + pronunciation_score

    data = {
        "score" : score,
        "weaks" : grammar_weak_ranking(errors),
        "total_score" : total_score,
        # "errors" : errors_json
    }

    # return HttpResponse(html)
    return render(request, 'evaluation/evaluation.html', data)
    #return HttpResponse(json.dumps(data, indent=2, ensure_ascii=False), content_type = "application/json; charset=utf-8")


# 1文ずつに分割
def split_sentances(texts):

    sentances = []
    for text in texts:
        splited = re.split('[.?!]', text)
        splited.remove('')
        sentances += [s if s[0] != ' ' else s[1:] for s in splited]

    return sentances

# sentances : 発話した文のリスト
def check_grammar(sentances):

    tool = language_tool_python.LanguageTool('en-US')
    
    errors = []
    for i, s in enumerate(sentances):
        # 文法をチェック
        matches = tool.check(s)

        # 定められたカテゴリに合うものだけを記録
        errors += [error(i, match)
                    for match in matches if (match.category in check_categories)]

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
                "message" : [e.to_json() for e in errors if e.errtype == p[0]][:3] # 3個まで例を表示
            }))

    # 出現回数上位三つを表示
    return dicl


# 以下，音声認識の評価

# 認証情報を外部ファイルから読み出す

COG_SERVICE_KEY=os.getenv('COG_SERVICE_KEY')
COG_SERVICE_REGION=os.getenv('COG_SERVICE_REGION')

def evaluationpage(request):
    result_json = evaluate_speech('What time is it now in Japan ?')

    context = {
        'result_json': result_json  # 評価結果をコンテキストに追加
    }

    return render(request, 'evaluation/evaluation.html', context)

# TODO 複数のwavファイルに対応
def evaluate_speech(script):

    # 評価パラメータ
    # 5段階評価，文・単語を評価
    pronunciation_config = speech_sdk.PronunciationAssessmentConfig(
        reference_text=script,
        grading_system=speech_sdk.PronunciationAssessmentGradingSystem.FivePoint,
        granularity=speech_sdk.PronunciationAssessmentGranularity.Word)

    # 諸設定
    speech_config = speech_sdk.SpeechConfig(COG_SERVICE_KEY, COG_SERVICE_REGION)
    audioFile = 'evaluation/content/time.wav'
    audio_config = speech_sdk.AudioConfig(filename=audioFile)
    speech_recognizer = speech_sdk.SpeechRecognizer(speech_config, audio_config)

    # 音声を評価
    pronunciation_config.apply_to(speech_recognizer)
    result = speech_recognizer.recognize_once()

    pronunciation_result = speech_sdk.PronunciationAssessmentResult(result)
    # pronunciation_result_json = result.properties.get(speech_sdk.PropertyId.SpeechServiceResponse_JsonResult)
    # print(pronunciation_result_json)
    # print('Accuracy score: {}, fluency score: {}, completeness score : {}, pronunciation score: {}'.format(
    #         pronunciation_result.accuracy_score, pronunciation_result.fluency_score,
    #         pronunciation_result.completeness_score, pronunciation_result.pronunciation_score
    #     ))

    words = []
    for word in pronunciation_result.words:
        words.append({
            "word": word.word,
            "score": word.accuracy_score
        })

    sorted_words = sorted(words, key=lambda x: x['score'])

    dic = dict({
            "score": pronunciation_result.pronunciation_score, # 総評的な点数
            "accuracy_score": pronunciation_result.accuracy_score, # 発音がどれだけ正しいのか
            "fluency_score": pronunciation_result.fluency_score, # 流暢さ（単語間隔など）
	        "completeness_score": pronunciation_result.completeness_score,  # 正解文章に対してどれだけちゃんと発音したか＝ぬけがないか
	        "words": sorted_words[:5]
        })

    return dic


