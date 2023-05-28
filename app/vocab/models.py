from django.db import models
# from login.models import User
from django.contrib.auth.models import User

class Wordbook(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='ユーザーID')
    word = models.CharField(max_length=50, primary_key=True, verbose_name='単語')
    meaning = models.TextField(blank=True, verbose_name='意味')
    pronunciation = models.CharField(max_length=50,blank=True, null=True, verbose_name='発音')
    category = models.CharField(max_length=50,blank=True, null=True, verbose_name='品詞')
    context = models.TextField(blank=True, null=True, verbose_name='文脈')

    class Meta:
        db_table = 'wordbook'
        ordering = ['word']
        verbose_name = '単語帳'
        verbose_name_plural = '単語帳'
        constraints = [
            models.UniqueConstraint(fields=['user_id', 'word'], name='unique_user_word')
        ]

    def __str__(self):
        return f"{self.word} ({self.pronunciation}) -  [{self.category}] {self.meaning}"