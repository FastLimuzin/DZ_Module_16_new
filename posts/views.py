from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Post
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect

class PostListView(ListView):
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'posts'

class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'posts/post_create.html'
    fields = ['title', 'content', 'image']
    success_url = reverse_lazy('posts:post_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Пост создан!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Заполните все поля!')
        return super().form_invalid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    template_name = 'posts/post_update.html'
    fields = ['title', 'content', 'image']
    success_url = reverse_lazy('posts:post_list')

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user

    def handle_no_permission(self):
        messages.error(self.request, 'Вы не можете редактировать чужой пост!')
        return redirect('posts:post_list')

    def form_valid(self, form):
        messages.success(self.request, 'Пост обновлён!')
        return super().form_valid(form)

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'posts/post_delete.html'
    success_url = reverse_lazy('posts:post_list')

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user

    def handle_no_permission(self):
        messages.error(self.request, 'Вы не можете удалить чужой пост!')
        return redirect('posts:post_list')

    def form_valid(self, form):
        messages.success(self.request, 'Пост удалён!')
        return super().form_valid(form)