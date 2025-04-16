from django.views.generic import FormView, TemplateView, UpdateView, View
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from .forms import CustomUserCreationForm, CustomUserUpdateForm  # Добавь новый импорт
from django.contrib.auth import login, logout, update_session_auth_hash
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import redirect
import random
import string

def generate_random_password():
    """Generate a random 8-character password."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(8))

class RegisterView(FormView):
    template_name = 'users/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('posts:post_list')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        try:
            send_mail(
                'Добро пожаловать!',
                f'Ваш аккаунт создан. Логин: {user.username}',
                'from@example.com',
                [user.email],
                fail_silently=True,
            )
        except Exception:
            pass
        messages.success(self.request, 'Регистрация прошла успешно!')
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)

class UserLoginView(LoginView):
    template_name = 'users/login.html'
    form_class = AuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        messages.success(self.request, 'Вы вошли!')
        return reverse_lazy('posts:post_list')

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'users/profile_update.html'
    form_class = CustomUserUpdateForm  # Используем новую форму
    success_url = reverse_lazy('users:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Профиль обновлён!')
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)

class PasswordUpdateView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'users/password_update.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('users:profile')

    def form_valid(self, form):
        response = super().form_valid(form)
        update_session_auth_hash(self.request, self.request.user)
        messages.success(self.request, 'Пароль обновлён!')
        return response

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)

class ResetPasswordView(LoginRequiredMixin, TemplateView):
    template_name = 'users/reset_password.html'

    def post(self, request, *args, **kwargs):
        new_password = generate_random_password()
        request.user.set_password(new_password)
        request.user.save()
        update_session_auth_hash(request, request.user)
        try:
            send_mail(
                'Ваш новый пароль',
                f'Ваш новый пароль: {new_password}',
                'from@example.com',
                [request.user.email],
                fail_silently=True,
            )
        except Exception:
            pass
        messages.success(request, 'Новый пароль сгенерирован и отправлен на ваш email.')
        return redirect('users:profile')

class UserLogoutView(View):
    template_name = 'users/logout.html'

    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, 'Вы вышли.')
        return redirect('posts:post_list')