from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm, PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
import random
import string

def generate_random_password():
    """Генерация случайного пароля: 8 символов (буквы + цифры)"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(8))

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Отправка письма с информацией о создании аккаунта
            send_mail(
                'Добро пожаловать!',
                f'Ваш аккаунт создан. Логин: {user.username}',
                'from@example.com',
                [user.email],
                fail_silently=False,
            )
            messages.success(request, 'Регистрация прошла успешно! Письмо отправлено на ваш email.')
            return redirect('posts:post_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Вы вошли!')
            return redirect('posts:post_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'users/profile.html', {'user': request.user})

@login_required
def profile_update(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён!')
            return redirect('users:profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserChangeForm(instance=request.user)
    return render(request, 'users/profile_update.html', {'form': form})

@login_required
def password_update(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)  # Обновляем сессию
            messages.success(request, 'Пароль обновлён!')
            return redirect('users:profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'users/password_update.html', {'form': form})

@login_required
def reset_password(request):
    if request.method == 'POST':
        new_password = generate_random_password()
        request.user.set_password(new_password)
        request.user.save()
        update_session_auth_hash(request, request.user)
        # Отправка нового пароля на почту
        send_mail(
            'Ваш новый пароль',
            f'Ваш новый пароль: {new_password}',
            'from@example.com',
            [request.user.email],
            fail_silently=False,
        )
        messages.success(request, 'Новый пароль сгенерирован и отправлен на ваш email.')
        return redirect('users:profile')
    return render(request, 'users/reset_password.html')

def user_logout(request):
    logout(request)
    messages.success(request, 'Вы вышли.')
    return redirect('posts:post_list')