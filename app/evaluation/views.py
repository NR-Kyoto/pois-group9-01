from django.shortcuts import render
from django.http import HttpResponse

from dataclasses import dataclass # 構造体
from deep_translator import GoogleTranslator # 翻訳
import language_tool_python # 文法チェック

import re # 正規表現

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

    index: int # 対象文の番号
    sentence: str
    start: int # 文内での開始位置
    end: int # 文内での終了位置
    message: str # エラーメッセージ
    suggestion: str # 正しい文

    def __init__(self, index, match):
        self.index = index
        self.sentence = match.sentence
        self.start = match.offset
        self.end = self.start + match.errorLength
        self.message = GoogleTranslator(source='auto',target='ja').translate(match.message)
        self.suggestion = match.sentence[:self.start] + match.replacements[0] + match.sentence[self.end:]

        # # カッコ内は除外して説明文を和訳 TODO
        # if match.message.find('“') == -1:
        #     self.message = GoogleTranslator(source='auto',target='ja').translate(match.message)
        # else:
        #     d_start = match.message.find('“') + 1
        #     d_end = match.message.find('”')
        #     trans = GoogleTranslator(source='auto',target='ja').translate(match.message[:d_start] + 'x' + match.message[d_end:])
        #     print(trans)
        #     b_start = trans.find('「') + 1
        #     b_end = trans.find('」')
        #     self.message = trans[:b_start] + match.message[d_start:d_end] + trans[b_end:]

    def to_html(self):
        html = '<div>'
        html += '<p>' + self.sentence[:self.start]
        html += '<strong>' + self.sentence[self.start:self.end] + '</strong>'
        html += self.sentence[self.end:] + '</p>'
        html += '<p>' + self.message + '</p>'
        html += '<p>fixed : ' + self.suggestion + '</p>'
        html += '</div>'
        return html

def evaluationpage(request):

    sentances = split_sentances(texts)
    errors = evaluate_grammar(sentances)

    # 文法のスコア（仮）：エラー数/文章数
    # 1以上 -> Poor
    # 0.5以上 -> Good
    # 0.3以下 -> Excellent
    score = len(errors) / len(sentances)

    # html = "error num : " + str(len(errors)) + " sentances : " + str(len(sentances))
    html = 'Evaluation : ' + 'Excellent' if score < 0.3 else 'Good' if score < 0.5 else 'Poor'
    html += ' (Score : ' + str(score) + ')'
    for e in errors:

        html += e.to_html()

    return HttpResponse(html)


# 1文ずつに分割
def split_sentances(texts):

    sentances = []
    for text in texts:
        splited = re.split('[.?!]', text)
        splited.remove('')
        sentances += [s if s[0] != ' ' else s[1:] for s in splited]

    return sentances

# sentances : 発話した文のリスト
def evaluate_grammar(sentances):

    tool = language_tool_python.LanguageTool('en-US')
    
    errors = []
    for i, s in enumerate(sentances):
        # 文法をチェック
        matches = tool.check(s)
        correct = tool.correct(s)

        # 定められたカテゴリに合うものだけを記録
        errors += [error(i, match)
                    for match in matches if (match.category in check_categories)]

    tool.close()

    return errors