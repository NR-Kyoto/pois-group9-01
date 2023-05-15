from django import forms
from .models import User

class UserForm(forms.ModelForm):
    user_id = forms.CharField(label='ユーザID')
    username = forms.CharField(label='ユーザ名')
    password = forms.CharField(widget=forms.PasswordInput(), label='パスワード')

    class Meta:
        model = User
        fields = ['user_id', 'username', 'password']