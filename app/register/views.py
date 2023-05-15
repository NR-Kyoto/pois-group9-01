from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserForm
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt

def register(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            user_id = form.cleaned_data.get('user_id')
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, user_id=user_id, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'アカウントが作成されました。{user_id}でログインしてください。')
                return redirect('home')
    else:
        form = UserForm()
    return render(request, 'register/register.html', {'form': form})
