from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required  # Добавьте эту строку
from .models import UserProfile, Text, RequestHistory
import json
import uuid
import random
import string
from django.views.decorators.http import require_http_methods
import re

def index(request):
    return render(request, 'cipher/index.html')

@login_required
def encrypt_page(request):
    return render(request, 'cipher/encrypt.html')

@login_required
def decrypt_page(request):
    return render(request, 'cipher/decrypt.html')

@login_required
def history_page(request):
    history = RequestHistory.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'cipher/history.html', {'history': history})

def prepare_key(key):
    key = ''.join(filter(str.isalpha, key.upper())).replace("J", "I")
    key = "".join(dict.fromkeys(key))
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    key += "".join(letter for letter in alphabet if letter not in key)
    return key

def playfair_cipher(key, text, mode='encrypt'):
    key_matrix = prepare_key(key)
    text = ''.join(filter(str.isalpha, text.upper())).replace("J", "I")
    if len(text) % 2 != 0:
        text += 'X'
    
    def find_position(letter):
        return divmod(key_matrix.index(letter), 5)
    
    result = ""
    for i in range(0, len(text), 2):
        row1, col1 = find_position(text[i])
        row2, col2 = find_position(text[i+1])
        
        if row1 == row2:
            if mode == 'encrypt':
                col1, col2 = (col1 + 1) % 5, (col2 + 1) % 5
            else:
                col1, col2 = (col1 - 1) % 5, (col2 - 1) % 5
        elif col1 == col2:
            if mode == 'encrypt':
                row1, row2 = (row1 + 1) % 5, (row2 + 1) % 5
            else:
                row1, row2 = (row1 - 1) % 5, (row2 - 1) % 5
        else:
            col1, col2 = col2, col1
        
        result += key_matrix[row1*5 + col1] + key_matrix[row2*5 + col2]
    
    return result

def generate_random_key(length=10):
    """
    Генерирует случайный ключ заданной длины.
    По умолчанию длина ключа - 10 символов.
    """
    alphabet = string.ascii_uppercase.replace('J', '')  # Удаляем 'J' из алфавита
    return ''.join(random.choice(alphabet) for _ in range(length))

def contains_cyrillic(text):
    return bool(re.search('[а-яА-Я]', text))

@csrf_exempt
def encrypt_text(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        text = data.get('text')
        key = data.get('key')
        
        if contains_cyrillic(text) or contains_cyrillic(key):
            return JsonResponse({'error': 'Шифр работает только с английским языком'}, status=400)
        
        if not key:
            key = generate_random_key()  # Генерируем случайный ключ, если он не предоставлен
        
        encrypted = playfair_cipher(key, text, mode='encrypt')
        if request.user.is_authenticated:
            RequestHistory.objects.create(user=request.user, request_type='Шифрование')
        return JsonResponse({'encrypted': encrypted, 'key': key})

@csrf_exempt
def decrypt_text(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        text = data.get('text')
        key = data.get('key')
        
        if contains_cyrillic(text) or contains_cyrillic(key):
            return JsonResponse({'error': 'Шифр работает только с английским языком'}, status=400)
        
        decrypted = playfair_cipher(key, text, mode='decrypt')
        if request.user.is_authenticated:
            RequestHistory.objects.create(user=request.user, request_type='Дешифрование')
        return JsonResponse({'decrypted': decrypted, 'key': key})

@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = User.objects.create_user(username=username, password=password)
        profile = UserProfile.objects.create(user=user)
        login(request, user)
        return JsonResponse({'token': str(profile.token)})

@csrf_exempt
def user_history(request):
    if request.method == 'GET':
        user = request.user
        history = RequestHistory.objects.filter(user=user).order_by('-timestamp')
        return JsonResponse({'history': list(history.values())})
    elif request.method == 'DELETE':
        user = request.user
        RequestHistory.objects.filter(user=user).delete()
        return JsonResponse({'message': 'История удалена'})

@csrf_exempt
@login_required
def change_password(request):
    if request.method == 'PATCH':
        data = json.loads(request.body)
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        user = request.user

        if not user.check_password(old_password):
            return JsonResponse({'error': 'Неверный текущий пароль'}, status=400)

        user.set_password(new_password)
        user.save()
        profile = UserProfile.objects.get(user=user)
        profile.token = uuid.uuid4()
        profile.save()
        return JsonResponse({'message': 'Пароль успешно изменен', 'new_token': str(profile.token)})
    return JsonResponse({'error': 'Неверный метод запроса'}, status=405)

@login_required
def profile_page(request):
    return render(request, 'cipher/profile.html')

@login_required
def text_list_page(request):
    return render(request, 'cipher/text_list.html')

@login_required
def add_text_page(request):
    return render(request, 'cipher/add_text.html')

@login_required
def view_text_page(request, text_id):
    text = Text.objects.get(id=text_id, user=request.user)
    return render(request, 'cipher/view_text.html', {
        'text': text,
        'show_key': text.key is not None,
        'is_encrypted': text.is_encrypted,
    })

def logout_view(request):
    logout(request)
    return redirect('index')

def register_page(request):
    return render(request, 'cipher/register.html')

@login_required
def manage_text(request, text_id=None):
    if request.method == 'POST':
        data = json.loads(request.body)
        title = data.get('title')
        content = data.get('content')
        original_content = data.get('original_content')
        key = data.get('key')
        is_encrypted = data.get('is_encrypted', False)
        is_manually_added = data.get('is_manually_added', True)  # Новый параметр
        text = Text.objects.create(
            user=request.user, 
            title=title, 
            content=content, 
            original_content=original_content, 
            key=key, 
            is_encrypted=is_encrypted,
            is_manually_added=is_manually_added
        )
        return JsonResponse({
            'id': text.id,
            'title': text.title,
            'content': text.content,
            'original_content': text.original_content,
            'key': text.key,
            'is_encrypted': text.is_encrypted,
            'is_manually_added': text.is_manually_added
        })
    elif request.method == 'PATCH' and text_id:
        data = json.loads(request.body)
        title = data.get('title')
        content = data.get('content')
        original_content = data.get('original_content')
        key = data.get('key')
        is_encrypted = data.get('is_encrypted')
        text = Text.objects.get(id=text_id, user=request.user)
        if title is not None:
            text.title = title
        if content is not None:
            text.content = content
        if original_content is not None:
            text.original_content = original_content
        if key is not None:
            text.key = key
        if is_encrypted is not None:
            text.is_encrypted = is_encrypted
        text.save()
        return JsonResponse({
            'id': text.id, 
            'title': text.title, 
            'content': text.content,
            'original_content': text.original_content,
            'key': text.key,
            'is_encrypted': text.is_encrypted
        })
    elif request.method == 'DELETE' and text_id:
        Text.objects.filter(id=text_id, user=request.user).delete()
        return JsonResponse({'message': 'Текст удален'})
    elif request.method == 'GET':
        if text_id:
            text = Text.objects.get(id=text_id, user=request.user)
            return JsonResponse({
                'id': text.id,
                'title': text.title,
                'content': text.content,
                'key': text.key
            })
        else:
            texts = Text.objects.filter(user=request.user)
            return JsonResponse({'texts': list(texts.values('id', 'title', 'content'))})

@require_http_methods(["GET"])
def generate_key(request):
    key = generate_random_key()
    return JsonResponse({'key': key})
