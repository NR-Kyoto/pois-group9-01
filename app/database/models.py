from django.db import models

class Users(models.Model):
    user_id = models.AutoField(primary_key=True,verbose_name='ユーザーID')
    username = models.CharField(max_length=50, unique=True,verbose_name='ユーザー名')
    password = models.CharField(max_length=50,verbose_name='パスワード')
    
    def __str__(self):
        return f"{self.username} ({self.user_id})"
    
    class Meta:
        db_table = 'user'
        ordering = ['user_id']
        verbose_name = 'ユーザー'
        verbose_name_plural = 'ユーザー'

class Wordbook(models.Model):
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE,verbose_name='ユーザーID')
    word = models.CharField(max_length=50, primary_key=True,verbose_name='単語')
    meaning = models.TextField(verbose_name='意味')
    pronunciation = models.CharField(max_length=50,blank=True, null=True,verbose_name='発音')
    category = models.CharField(max_length=50,blank=True, null=True,verbose_name='品詞')
    context = models.TextField(blank=True, null=True,verbose_name='文脈')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user_id', 'word'], name='unique_user_word')
        ]

    def __str__(self):
        return f"{self.word} ({self.pronunciation}) -  [{self.category}] {self.meaning}"
    
    class Meta:
        db_table = 'wordbook'
        ordering = ['word']
        verbose_name = '単語帳'
        verbose_name_plural = '単語帳'


class Chat(models.Model):
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE,verbose_name='ユーザーID')
    time = models.DateTimeField(primary_key=True,verbose_name='日時')
    contents = models.TextField(verbose_name='会話内容')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user_id', 'time'], name='unique_user_time')
        ]

    def __str__(self):
        return f"{self.user_id.username} ({self.time}) - {self.contents}"
    
    class Meta:
        db_table = 'chat'
        ordering = ['-time']
        verbose_name = '会話'
        verbose_name_plural = '会話'