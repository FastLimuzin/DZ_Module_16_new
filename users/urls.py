from django.urls import path
from . import views

app_name = 'users'
urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('profile/password/', views.password_update, name='password_update'),
    path('profile/reset/', views.reset_password, name='reset_password'),
    path('logout/', views.user_logout, name='logout'),
]