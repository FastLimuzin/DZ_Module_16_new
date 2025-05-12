from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/update/', views.ProfileUpdateView.as_view(), name='profile_update'),
    path('password/update/', views.PasswordUpdateView.as_view(), name='password_update'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset_password'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<str:username>/', views.UserDetailView.as_view(), name='user_detail'),
]