# Generated by Django 3.2 on 2023-05-16 05:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('login', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Wordbook',
            fields=[
                ('word', models.CharField(max_length=50, primary_key=True, serialize=False, verbose_name='単語')),
                ('meaning', models.TextField(verbose_name='意味')),
                ('pronunciation', models.CharField(blank=True, max_length=50, null=True, verbose_name='発音')),
                ('category', models.CharField(blank=True, max_length=50, null=True, verbose_name='品詞')),
                ('context', models.TextField(blank=True, null=True, verbose_name='文脈')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='login.user', verbose_name='ユーザーID')),
            ],
            options={
                'verbose_name': '単語帳',
                'verbose_name_plural': '単語帳',
                'db_table': 'wordbook',
                'ordering': ['word'],
            },
        ),
        migrations.AddConstraint(
            model_name='wordbook',
            constraint=models.UniqueConstraint(fields=('user_id', 'word'), name='unique_user_word'),
        ),
    ]
