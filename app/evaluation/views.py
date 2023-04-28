from django.shortcuts import render
from django.http import HttpResponse

from dataclasses import dataclass # 構造体
from deep_translator import GoogleTranslator # 翻訳
import language_tool_python # 文法チェック

check_categories = ['CONFUSED_WORDS', 'GRAMMAR', 'REPETITIONS', 'TYPOS']

@dataclass(init=False)
class error:

    # error_type: int
    index: int # 対象文の番号
    sentence: str
    start: int # 文内での開始位置
    end: int # 文内での終了位置
    message: str # エラーメッセージ
    suggestion: str # 正しい文

    def __init__(self, index, match, text):
        # error_type = 
        self.index = index
        self.sentence = match.sentence
        self.start = match.offset - text.index(match.sentence)
        self.end = self.start + match.errorLength
        self.message = GoogleTranslator(source='auto',target='ja').translate(match.message)
        self.suggestion = match.sentence[:self.start] + match.replacements[0] + match.sentence[self.end:]

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

    sentances = [
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

    errors = evaluate_grammar(sentances)

    html = "error num : " + str(len(errors))
    for e in errors:

        # print(match)

        # html += '<div>'
        # html += '<p>' + match.category + '</p>'
        # output = str(match)
        # html += output.replace('\n', '<br>')

        # html += '</div>'

        html += e.to_html()

    return HttpResponse(html)

# texts : 発話した文章のリスト
def evaluate_grammar(texts):

    tool = language_tool_python.LanguageTool('en-US')
    
    errors = []
    for i, text in enumerate(texts):
        # 文法をチェック
        matches = tool.check(text)
        correct = tool.correct(text)

        # 定められたカテゴリに合うものだけを記録
        errors += [error(i, match, text)
                    for match in matches if (match.category in check_categories)]

    tool.close()

    return errors

