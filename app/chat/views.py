from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import speech_recognition as sr
from gtts import gTTS
import json, base64, io, subprocess, tempfile
import openai
import os
import re
from .models import Audio

openai.api_key = os.getenv("OPENAI_API_KEY")

model_engine = "gpt-3.5-turbo"


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

    with tempfile.NamedTemporaryFile(delete=True, suffix="_webm") as audio_webm:
        command = ['ffmpeg', '-y', '-i', 'gTTS_test.mp3','-f', 'webm', str(audio_webm.name)]
        subprocess.run(command)

        with open(str(audio_webm.name), 'rb') as f:
            print(type(f))
            audio_b = f.read()
            audio_base64 = base64.b64encode(audio_b).decode('utf-8')

    return audio_base64

def start_chat():
    prompt = "Please chat with me in super-easy English little by little. I am a foreigner. I am alone. I understand little English. Please talk to me like I'm a three-year-old. I only understand one sentence at a time. Please start a chat with me."

    message_list = [{"role": "system", "content": prompt}]

    return generate_text(message_list)

#chatgptにアクセスするための関数
def generate_text(message_list):

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=message_list,
            max_tokens=100
        )
    except Exception as e:
        print(e)
        return "AI is currently unavailable"

    chat_message = response["choices"][0]["message"]

    chat = chat_message["content"]
    l = chat.split()
    num = len(l)

    if num>30:
        message_len = len(message_list)
        message_list[message_len-1]["content"] = message_list[message_len-1]["content"]+" in 20 words"
        chat = generate_text(message_list)
        
    return chat

def clean_message_list(message_list_input):
    message_list=[]

    for message in message_list_input:
        if message["isAssistant"]==True:
            role = "assistant"
        else:
            role = "user"
        content_temp = message["lines"]
        content = re.sub("\n", " ", content_temp)
        content = content.strip()

        message_list.append({"role":role,"content":content})
    
    return message_list

#for development below, remove before launch
def mock(request):
    return render(request, 'chat/index.html')

def mock_post(request):
    if request.method == 'POST':
        data = request.POST["text_input"]
        #data2 = [json.loads(e) for e in request.POST["chat_history"]]
        data2 = json.loads(request.POST["chat_history"])
        data_audio = request.POST["audio64"] #base64 encoded audio (webm)

        message_list = clean_message_list(data2)
        message_list.append({"role":"user","content":data})
        gpt = generate_text(message_list)

        Audio.objects.create(text=data, fields={"audio":data_audio})
        #gpt = "gpt text" #for testing

        audio_base64 = text_to_speech(gpt)

        new_entries = [{"speaker": "user", "isAssistant": False, "lines":data, "audio": data_audio},
                          {"speaker": "assistant", "isAssistant": True, "lines": gpt, "audio": audio_base64}]
        data2.extend(new_entries)
        res = {"chat": data2}
        return JsonResponse(res)

def mock_post_audio(request):
    if request.method == 'POST':
        data = request.POST["audio"]
        #print(data)
        #decode data of base64 to .wav file

        with tempfile.NamedTemporaryFile(delete=True, suffix="_webm") as audio_webm:
            audio_webm.write(base64.b64decode(data))
            #print(type(audio_webm))
            with tempfile.NamedTemporaryFile(delete=True, suffix="_wav") as audio_wav:
                command = ['ffmpeg', '-y', '-i', str(audio_webm.name),'-f', 'wav', '-c:a', 'pcm_s16le', str(audio_wav.name)]
                subprocess.run(command)

                text = speech_to_text(audio_wav.name)

        print("audio text : " + text)

    return JsonResponse({"text": text ,"audio":data})#audio response is not necessarily here

def mock_init(request):
    if request.method == 'POST':
        gpt = start_chat()
        #gpt = generate_text(message_list)
        #gpt = "gpt text" #for testing

        audio_base64 = text_to_speech(gpt)

        new_entries = [{"speaker": "assistant", "isAssistant": True, "lines": gpt, "audio": audio_base64}]
        res = {"chat": new_entries}
        return JsonResponse(res)


def mock_post_selected(request):
    if request.method == 'POST':
        selected = json.loads(request.POST["selected"])
        text = selected["text"]
        context = selected["context"]

        #do something with data

        print("selected text : " + text)
        print("selected context : " + context)

        meanings = "some randome meanings text or json"
        res = {"text": text, "meaning": meanings, "category": "noun", "word_flag": False}
        return JsonResponse(res)
