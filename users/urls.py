from django.urls import path
from .views import RegisterView, UserLoginView, ProfileView, ProfileUpdateView, PasswordUpdateView, ResetPasswordView, UserLogoutView

app_name = 'users'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile_update'),
    path('password/update/', PasswordUpdateView.as_view(), name='password_update'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('logout/', UserLogoutView.as_view(), name='logout'),  # Укажем as_view() для классового представления
]