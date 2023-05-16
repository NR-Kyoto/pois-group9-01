from django.shortcuts import render
from django.http import HttpResponse
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

model_engine = "gpt-3.5-turbo"

def chatpage(request):
    return HttpResponse("chat world")

def start_chat():
    prompt = "Please chat with me in super-easy English little by little. I am a foreigner. I am alone. I understand little English. Please talk to me like I'm a three-year-old. I only understand one sentence at a time. Please start a chat with me."

    message_list = [{"role": "system", "content": prompt}]

    return generate_text(message_list)

#chatgptにアクセスするための関数
def generate_text(message_list):

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=message_list
        )
    except Exception as e:
        print(e)
        return "AI is currently unavailable"

    chat_message = [response["choices"][0]["message"]]
    return chat_message

