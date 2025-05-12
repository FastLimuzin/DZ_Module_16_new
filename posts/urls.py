from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('create/', views.PostCreateView.as_view(), name='post_create'),
    path('post/<int:pk>/update/', views.PostUpdateView.as_view(), name='post_update'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    path('post/<int:pk>/toggle-active/', views.toggle_post_active, name='toggle_active'),
    path('post/<int:pk>/review/', views.ReviewCreateView.as_view(), name='review_create'),
    path('review/<slug:review_slug>/', views.ReviewDetailView.as_view(), name='review_detail'),
]