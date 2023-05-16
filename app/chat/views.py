from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json

def chatpage(request):
    return HttpResponse("chat world")

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
