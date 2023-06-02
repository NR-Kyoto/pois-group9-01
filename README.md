# pois-group9-01
Practice of Information Systems前半のグループ9用のリポジトリ

## dockerの使い方
docker-compose.ymlと同じ階層のフォルダに入り

```
docker compose up
```

を実行

もう一つのタブでターミナルを開き

```
docker compose exec django bash
```

でコンテナに接続できる

Webサーバーの起動は

```
python manage.py runserver 0:8000
```


## 新しいアプリケーションの作り方

```
python manage.py startapp アプリケーション名
```

english_bot_2000/settings.pyのINSTALLED_APPSに``アプリケーション名.apps.アプリケーション名Config``を追加（自動生成される）

### Model

必要ならモデルを編集してデータベースを作成

アプリケーション名/models.py

```
from django.conf import settings
from django.db import models

class オブジェクト名(models.Model):
    データベースの属性
    メソッド
```

モデルの変更を通知

```
python manage.py makemigrations アプリケーション名
```

データベース作成

```
python manage.py migrate アプリケーション名
```

### Template

アプリケーションのフォルダ内にtempleates/アプリケーション名と2階層分のフォルダを作成．
さらに，適当なHTMLファイルを作成する

### View

アプリケーション名/views.pyに以下を追加

```
def 関数名(request):
    return render(request, 'アプリケーション名/～.html', {})
```

### URL

english_bot_2000/urls.pyのurlpatternsに``path('任意のURLパターン', include('アプリケーション名.urls')),``を追加

アプリケーション名/urls.pyを作成以下のように記述

```
from django.urls import path
from . import views

urlpatterns = [
    path('', views.ビューの関数, name='URLパスの名前'),
]
```
