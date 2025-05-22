from django.views.generic import FormView, TemplateView, UpdateView, View, ListView, DetailView
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm, CustomUserUpdateForm
from django.contrib.auth import login, logout, update_session_auth_hash
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import redirect
import random
import string
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator

def generate_random_password():
    """
    Генерирует случайный пароль длиной 8 символов.

    Возвращает:
        str: Случайный пароль.
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(8))

class RegisterView(FormView):
    """
    Регистрирует нового пользователя.

    Атрибуты:
        template_name: Шаблон для формы регистрации.
        form_class: Форма для создания пользователя.
        success_url: URL после успешной регистрации.
    """
    template_name = 'users/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('posts:post_list')

    def form_valid(self, form):
        """
        Сохраняет пользователя и отправляет email.

        Аргументы:
            form: Форма регистрации.

        Возвращает:
            HttpResponse: Перенаправление.
        """
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
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Обрабатывает ошибки формы.

        Аргументы:
            form: Форма с ошибками.

        Возвращает:
            HttpResponse: Ошибка.
        """
        return super().form_invalid(form)

class UserLoginView(LoginView):
    """
    Аутентифицирует пользователя.

    Атрибуты:
        template_name: Шаблон для формы входа.
        form_class: Форма для входа.
        redirect_authenticated_user: Перенаправление авторизованных.
    """
    template_name = 'users/login.html'
    form_class = AuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        """
        Возвращает URL после успешного входа.

        Возвращает:
            str: URL для перенаправления.
        """
        return reverse_lazy('posts:post_list')

    def form_invalid(self, form):
        """
        Обрабатывает ошибки формы.

        Аргументы:
            form: Форма с ошибками.

        Возвращает:
            HttpResponse: Ошибка.
        """
        return super().form_invalid(form)

class ProfileView(LoginRequiredMixin, TemplateView):
    """
    Отображает профиль пользователя.

    Атрибуты:
        template_name: Шаблон профиля.
    """
    template_name = 'users/profile.html'

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    Обновляет профиль пользователя.

    Атрибуты:
        template_name: Шаблон для формы.
        form_class: Форма для обновления.
        success_url: URL после обновления.
    """
    template_name = 'users/profile_update.html'
    form_class = CustomUserUpdateForm
    success_url = reverse_lazy('users:profile')

    def get_object(self):
        """
        Возвращает текущего пользователя.

        Возвращает:
            User: Текущий пользователь.
        """
        return self.request.user

    def form_valid(self, form):
        """
        Сохраняет обновлённый профиль.

        Аргументы:
            form: Форма профиля.

        Возвращает:
            HttpResponse: Перенаправление.
        """
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Обрабатывает ошибки формы.

        Аргументы:
            form: Форма с ошибками.

        Возвращает:
            HttpResponse: Ошибка.
        """
        return super().form_invalid(form)

class PasswordUpdateView(LoginRequiredMixin, PasswordChangeView):
    """
    Обновляет пароль пользователя.

    Атрибуты:
        template_name: Шаблон для формы.
        form_class: Форма для смены пароля.
        success_url: URL после смены.
    """
    template_name = 'users/password_update.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('users:profile')

    def form_valid(self, form):
        """
        Сохраняет новый пароль.

        Аргументы:
            form: Форма смены пароля.

        Возвращает:
            HttpResponse: Перенаправление.
        """
        response = super().form_valid(form)
        update_session_auth_hash(self.request, self.request.user)
        return response

    def form_invalid(self, form):
        """
        Обрабатывает ошибки формы.

        Аргументы:
            form: Форма с ошибками.

        Возвращает:
            HttpResponse: Ошибка.
        """
        return super().form_invalid(form)

class ResetPasswordView(LoginRequiredMixin, TemplateView):
    """
    Сбрасывает пароль пользователя.

    Атрибуты:
        template_name: Шаблон для сброса.
    """
    template_name = 'users/reset_password.html'

    def post(self, request, *args, **kwargs):
        """
        Генерирует новый пароль и отправляет email.

        Аргументы:
            request: HTTP-запрос.
            *args, **kwargs: Дополнительные аргументы.

        Возвращает:
            HttpResponse: Перенаправление.
        """
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
        return redirect('users:profile')

class UserLogoutView(View):
    """
    Выполняет выход пользователя.
    """
    def get(self, request, *args, **kwargs):
        """
        Завершает сессию пользователя.

        Аргументы:
            request: HTTP-запрос.
            *args, **kwargs: Дополнительные аргументы.

        Возвращает:
            HttpResponse: Перенаправление.
        """
        logout(request)
        return redirect('users:login')

class UserListView(LoginRequiredMixin, ListView):
    """
    Отображает список пользователей с пагинацией.

    Атрибуты:
        model: Модель User.
        template_name: Шаблон для списка.
        context_object_name: Имя объекта в шаблоне.
        login_url: URL для входа.
        paginate_by: Количество пользователей на странице.
    """
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    login_url = reverse_lazy('users:login')
    paginate_by = 5

class UserDetailView(LoginRequiredMixin, DetailView):
    """
    Отображает детальную информацию о пользователе.

    Атрибуты:
        model: Модель User.
        template_name: Шаблон для отображения.
        context_object_name: Имя объекта в шаблоне.
        login_url: URL для входа.
    """
    model = User
    template_name = 'users/user_detail.html'
    context_object_name = 'user'
    login_url = reverse_lazy('users:login')

    def get_object(self):
        """
        Получает пользователя по имени.

        Возвращает:
            User: Объект пользователя.
        """
        return User.objects.get(username=self.kwargs['username'])