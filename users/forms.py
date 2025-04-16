from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Обязательное поле.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class CustomUserUpdateForm(UserChangeForm):
    password = None  # Убираем поле пароля, оно не нужно в этой форме

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        labels = {
            'username': 'Имя пользователя',
            'email': 'Адрес электронной почты',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
        }
        help_texts = {
            'username': 'Обязательное поле. Не более 150 символов. Только буквы, цифры и @/./+/-/_',
        }