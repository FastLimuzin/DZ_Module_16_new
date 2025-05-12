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
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)

class UserLoginView(LoginView):
    template_name = 'users/login.html'
    form_class = AuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('posts:post_list')

    def form_invalid(self, form):
        return super().form_invalid(form)

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'users/profile_update.html'
    form_class = CustomUserUpdateForm
    success_url = reverse_lazy('users:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)

class PasswordUpdateView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'users/password_update.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('users:profile')

    def form_valid(self, form):
        response = super().form_valid(form)
        update_session_auth_hash(self.request, self.request.user)
        return response

    def form_invalid(self, form):
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
        return redirect('users:profile')

class UserLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('users:login')

class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    login_url = reverse_lazy('users:login')
    paginate_by = 5  # Пагинация: 5 пользователей на страницу

class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/user_detail.html'
    context_object_name = 'user'
    login_url = reverse_lazy('users:login')

    def get_object(self):
        return User.objects.get(username=self.kwargs['username'])