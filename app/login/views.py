from .forms import SignupForm, LoginForm
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

class MySignupView(CreateView):
    template_name = 'login/signup.html'
    form_class = SignupForm
    success_url = '/home/'
    
    def form_valid(self, form):

        # 妥当性の判断＆レコードの保存
        result = super().form_valid(form)

        # login 
        user = self.object
        login(self.request, user)
        return result

class MyLoginView(LoginView):
    template_name = 'login/login.html'
    form_class = LoginForm

class MyLogoutView(LogoutView):
    template_name = 'login/logout.html'

# class MyUserView(LoginRequiredMixin, TemplateView):
#     template_name = 'login/user.html'
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['user'] = self.request.user
#         return context

# class MyOtherView(LoginRequiredMixin, TemplateView):
#     template_name = 'login/other.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['users'] = User.objects.exclude(username=self.request.user.username)
#         return context