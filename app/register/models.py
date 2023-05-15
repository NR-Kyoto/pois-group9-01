from django.db import models

class User(models.Model):
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