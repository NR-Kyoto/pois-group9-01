from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import UserForm
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def loginpage(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user_id = form.cleaned_data['user_id']
            password = form.cleaned_data['password']
            user = authenticate(request, user_id=user_id, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                return redirect('login')
    else:
        form = UserForm()
    return render(request, 'login/login.html', {'form': form})


