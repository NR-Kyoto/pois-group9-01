from django.shortcuts import render
from django.http import HttpResponse
import speech_recognition as sr
from gtts import gTTS

def chatpage(request):
    return HttpResponse("chat world")

def speech_to_text(audio_file):
    r = sr.Recognizer()

    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)

    try:
        text = r.recognize_google(audio, language='en-US')
    except sr.UnknownValueError:
        text = "Google Speech Recognition could not understand audio"
    except sr.RequestError as e:
        text = "Could not request results from Google Speech Recognition service"

    return text

def text_to_speech(text):
    message = text
    tts = gTTS(message, lang='en')
    tts.save('gTTS_test.mp3')