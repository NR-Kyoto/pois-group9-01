from django.contrib import admin
from login.models import User
from vocab.models import Wordbook

admin.site.register(User)
admin.site.register(Wordbook)