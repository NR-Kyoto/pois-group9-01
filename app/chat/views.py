from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import speech_recognition as sr
from gtts import gTTS
import json, base64

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
#for development below, remove before launch
def mock(request):
    return render(request, 'chat/index.html')

def mock_post(request):
    if request.method == 'POST':
        data = request.POST["text_input"]
        #data2 = [json.loads(e) for e in request.POST["chat_history"]]
        data2 = json.loads(request.POST["chat_history"])
        #do something with data

        
        new_entries = [{"speaker": "user", "isAssistant": False, "text":data},
                          {"speaker": "assistant", "isAssistant": True, "text": data + "ですね。"}]
        data2.extend(new_entries)
        res = {"chat": data2}
        return JsonResponse(res)

def mock_post_audio(request):
    if request.method == 'POST':
        data = request.POST["audio"]
        print(data)
        #decode data of base64 to .wav file
        audio_wav = base64.b64decode(data)
        

        #data(audio file) to base64
        #audio_base64 = base64.b64encode(data).decode('utf-8')
        
    return JsonResponse({"text":"text from audio","audio":data})#audio response is not necessarily here
