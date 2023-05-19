from django.shortcuts import render, get_object_or_404, redirect
from .forms import WordbookForm
from .models import Wordbook
from django.db.models import Q

def vocabpage(request):
    if request.method == 'POST':
        form = WordbookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('vocabpage')
    else:
        form = WordbookForm()
    
    search_query = request.GET.get('search_query', '')
    wordbook_data = Wordbook.objects.filter(
        Q(word__icontains=search_query) | Q(meaning__icontains=search_query)
    ).order_by('word') 

    context = {'wordbook_data': wordbook_data, 'form': form}
    return render(request, 'vocab/vocab.html', context)

def add_word(request):
    if request.method == 'POST':
        form = WordbookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('vocabpage')
    else:
        form = WordbookForm()
    return render(request, 'vocab/add_word.html', {'form': form})

def edit_word(request, user_id_id, word):
    word = get_object_or_404(Wordbook, user_id_id=user_id_id, word=word)
    if request.method == 'POST':
        form = WordbookForm(request.POST, instance=word)
        if form.is_valid():
            form.save()
            return redirect('vocabpage')
    else:
        form = WordbookForm(instance=word)
    return render(request, 'vocab/edit_word.html', {'form': form, 'user_id_id': user_id_id, 'word': word})


def delete_word(request, user_id_id, word):
    word = get_object_or_404(Wordbook, user_id_id=user_id_id, word=word)
    if request.method == 'POST':
        word.delete()
        return redirect('vocabpage')
    return render(request, 'vocab/delete_word.html', {'word': word})
