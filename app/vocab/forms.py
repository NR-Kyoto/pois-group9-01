from django import forms
from .models import Wordbook

class WordbookForm(forms.ModelForm):

    class Meta:
        model = Wordbook
        fields = ('user_id', 'word', 'meaning', 'pronunciation', 'category', 'context')

