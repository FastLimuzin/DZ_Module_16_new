from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('posts:post_list')
        else:
            messages.error(request, 'Ошибка регистрации.')
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.user
            login(request, user)
            messages.success(request, 'Вы вошли!')
            return redirect('posts:post_list')
        else:
            messages.error(request, 'Неверный логин или пароль.')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def profile(request):
    if request.user.is_authenticated:
        return render(request, 'users/profile.html', {'user': request.user})
    else:
        messages.error(request, 'Войдите, чтобы увидеть профиль.')
        return redirect('users:login')

def user_logout(request):
    logout(request)
    messages.success(request, 'Вы вышли.')
    return redirect('posts:post_list')