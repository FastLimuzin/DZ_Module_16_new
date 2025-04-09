from django.urls import path
from . import views

app_name = 'users'
urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/update/', views.ProfileUpdateView.as_view(), name='profile_update'),
    path('profile/password/', views.PasswordUpdateView.as_view(), name='password_update'),
    path('profile/reset/', views.ResetPasswordView.as_view(), name='reset_password'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
]