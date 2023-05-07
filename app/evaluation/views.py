from django.shortcuts import render
from django.http import HttpResponse

import json
import azure.cognitiveservices.speech as speech_sdk

import os

# 認証情報を外部ファイルから読み出す

COG_SERVICE_KEY=os.getenv('COG_SERVICE_KEY')
COG_SERVICE_REGION=os.getenv('COG_SERVICE_REGION')

def evaluationpage(request):
    print(COG_SERVICE_KEY)
    result_json = evaluate_speech('What time is it now in Japan ?')

    return HttpResponse(result_json)

# TODO 複数のwavファイルに対応
def evaluate_speech(script):

    # script = 'What time is it now in Japan ?'

    # 評価パラメータ
    # 5段階評価，文・単語・音節を評価
    pronunciation_config = speech_sdk.PronunciationAssessmentConfig(
        reference_text=script,
        grading_system=speech_sdk.PronunciationAssessmentGradingSystem.FivePoint,
        granularity=speech_sdk.PronunciationAssessmentGranularity.Phoneme)

    # 諸設定
    speech_config = speech_sdk.SpeechConfig(COG_SERVICE_KEY, COG_SERVICE_REGION)
    audioFile = 'evaluation/content/time.wav'
    audio_config = speech_sdk.AudioConfig(filename=audioFile)
    speech_recognizer = speech_sdk.SpeechRecognizer(speech_config, audio_config)

    # 音声を評価
    pronunciation_config.apply_to(speech_recognizer)
    result = speech_recognizer.recognize_once()

    pronunciation_result = speech_sdk.PronunciationAssessmentResult(result)
    pronunciation_result_json = result.properties.get(speech_sdk.PropertyId.SpeechServiceResponse_JsonResult)
    # print(pronunciation_result_json)
    # print('Accuracy score: {}, fluency score: {}, completeness score : {}, pronunciation score: {}'.format(
    #         pronunciation_result.accuracy_score, pronunciation_result.fluency_score,
    #         pronunciation_result.completeness_score, pronunciation_result.pronunciation_score
    #     ))

    return pronunciation_result_json
