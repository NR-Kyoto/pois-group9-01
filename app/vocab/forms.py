from django import forms
from .models import Wordbook

class WordbookForm(forms.ModelForm):

    class Meta:
        model = Wordbook
        exclude = ('user_id', )

