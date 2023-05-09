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

    return generate_text(prompt)

#chatgptにアクセスするための関数
def generate_text(prompt):

    try:
        response = openai.Completion.create(
            engine=model_engine,
            prompt=prompt,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.7,
        )
    except Exception as e:
        print(e)
        return "AI is currently unavailable"

    message = response.choices[0].text.strip()
    return message

