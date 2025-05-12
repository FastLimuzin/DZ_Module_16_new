from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Post
from .forms import PostForm, PostOriginFormSet
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings

class PostListView(ListView):
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'posts'
    ordering = ['-created_at']

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Post.objects.filter(is_active=True)
        elif self.request.user.has_perm('posts.change_post'):
            return Post.objects.all()
        return Post.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_change'] = self.request.user.has_perm('posts.change_post')
        context['can_delete'] = self.request.user.has_perm('posts.delete_post')
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'

    def get_object(self):
        obj = super().get_object()
        if self.request.user.is_authenticated and self.request.user != obj.author:
            obj.views += 1
            obj.save()
            if obj.views % 100 == 0 and obj.author and obj.author.email:
                send_mail(
                    subject=f'Ваш пост "{obj.title}" набрал {obj.views} просмотров!',
                    message=f'Поздравляем! Ваш пост "{obj.title}" достиг {obj.views} просмотров.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[obj.author.email],
                    fail_silently=True,
                )
        if not obj.is_active and not self.request.user.has_perm('posts.change_post'):
            raise HttpResponseForbidden("Этот пост неактивен и доступен только модераторам.")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_change'] = self.request.user.has_perm('posts.change_post')
        context['can_delete'] = self.request.user.has_perm('posts.delete_post')
        return context

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'posts/post_create.html'
    form_class = PostForm
    success_url = reverse_lazy('posts:post_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['origin_formset'] = PostOriginFormSet(self.request.POST, self.request.FILES)
        else:
            context['origin_formset'] = PostOriginFormSet()
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        context = self.get_context_data()
        origin_formset = context['origin_formset']
        if origin_formset.is_valid():
            self.object = form.save()
            origin_formset.instance = self.object
            origin_formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    template_name = 'posts/post_update.html'
    form_class = PostForm
    success_url = reverse_lazy('posts:post_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if not self.request.user.has_perm('posts.change_post'):
            for field in ['is_active', 'author', 'views']:
                if field in form.fields:
                    del form.fields[field]
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['origin_formset'] = PostOriginFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            context['origin_formset'] = PostOriginFormSet(instance=self.object)
        return context

    def test_func(self):
        post = self.get_object()
        if self.request.user.has_perm('posts.change_post'):
            return True
        return post.author == self.request.user

    def handle_no_permission(self):
        return redirect('posts:post_list')

    def form_valid(self, form):
        context = self.get_context_data()
        origin_formset = context['origin_formset']
        if origin_formset.is_valid():
            self.object = form.save()
            origin_formset.instance = self.object
            origin_formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'posts/post_delete.html'
    success_url = reverse_lazy('posts:post_list')

    def test_func(self):
        post = self.get_object()
        if self.request.user.has_perm('posts.delete_post'):
            return True
        return post.author == self.request.user

    def handle_no_permission(self):
        return redirect('posts:post_list')

    def form_valid(self, form):
        return super().form_valid(form)

@permission_required('posts.change_post', raise_exception=True)
def toggle_post_active(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.is_active = not post.is_active
    post.save()
    return redirect('posts:post_list')