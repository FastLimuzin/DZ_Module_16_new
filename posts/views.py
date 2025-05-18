from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Post, Review, Origin
from .forms import PostForm, PostOriginFormSet, ReviewForm
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseForbidden
from django.core.mail import send_mail
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q

class PostListView(ListView):
    """
    Отображает список постов с пагинацией.

    Атрибуты:
        model: Модель Post.
        template_name: Шаблон для отображения списка.
        context_object_name: Имя объекта в шаблоне.
        ordering: Сортировка по дате создания (убывание).
        paginate_by: Количество постов на странице.
    """
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'posts'
    ordering = ['-created_at']
    paginate_by = 5

    def get_queryset(self):
        """
        Возвращает набор постов в зависимости от прав пользователя.

        Возвращает:
            QuerySet: Посты, доступные пользователю.
        """
        if not self.request.user.is_authenticated:
            return Post.objects.filter(is_active=True)
        elif self.request.user.has_perm('posts.change_post'):
            return Post.objects.all()
        return Post.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительные данные в контекст шаблона.

        Аргументы:
            **kwargs: Дополнительные аргументы.

        Возвращает:
            dict: Контекст для шаблона.
        """
        context = super().get_context_data(**kwargs)
        context['can_change'] = self.request.user.has_perm('posts.change_post')
        context['can_delete'] = self.request.user.has_perm('posts.delete_post')
        return context

class SearchView(ListView):
    """
    Выполняет поиск постов по заголовку или месту происхождения.

    Атрибуты:
        model: Модель Post.
        template_name: Шаблон для отображения результатов.
        context_object_name: Имя объекта в шаблоне.
        paginate_by: Количество результатов на странице.
    """
    model = Post
    template_name = 'posts/search_results.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        """
        Выполняет поиск по заголовку поста или месту происхождения.

        Возвращает:
            QuerySet: Посты, соответствующие запросу.
        """
        query = self.request.GET.get('q', '')
        if not query:
            return Post.objects.none()

        if self.request.user.is_authenticated and self.request.user.has_perm('posts.change_post'):
            posts = Post.objects.filter(
                Q(title__icontains=query) |
                Q(origins__origin__icontains=query)
            ).distinct()
        else:
            posts = Post.objects.filter(
                Q(title__icontains=query) |
                Q(origins__origin__icontains=query),
                is_active=True
            ).distinct()
        return posts

    def get_context_data(self, **kwargs):
        """
        Добавляет поисковый запрос в контекст.

        Аргументы:
            **kwargs: Дополнительные аргументы.

        Возвращает:
            dict: Контекст для шаблона.
        """
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context

class PostDetailView(DetailView):
    """
    Отображает детальную информацию о посте.

    Атрибуты:
        model: Модель Post.
        template_name: Шаблон для отображения.
        context_object_name: Имя объекта в шаблоне.
    """
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'

    def get_object(self):
        """
        Получает объект поста и увеличивает счётчик просмотров.

        Возвращает:
            Post: Объект поста.
        """
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
        """
        Добавляет данные для формы отзыва и список отзывов.

        Аргументы:
            **kwargs: Дополнительные аргументы.

        Возвращает:
            dict: Контекст для шаблона.
        """
        context = super().get_context_data(**kwargs)
        context['can_change'] = self.request.user.has_perm('posts.change_post')
        context['can_delete'] = self.request.user.has_perm('posts.delete_post')
        context['review_form'] = ReviewForm()
        context['reviews'] = self.object.reviews.all()
        return context

class PostCreateView(LoginRequiredMixin, CreateView):
    """
    Создаёт новый пост.

    Атрибуты:
        model: Модель Post.
        template_name: Шаблон для формы.
        form_class: Форма для создания поста.
        success_url: URL после успешного создания.
    """
    model = Post
    template_name = 'posts/post_create.html'
    form_class = PostForm
    success_url = reverse_lazy('posts:post_list')

    def get_context_data(self, **kwargs):
        """
        Добавляет формсет для происхождения.

        Аргументы:
            **kwargs: Дополнительные аргументы.

        Возвращает:
            dict: Контекст для шаблона.
        """
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['origin_formset'] = PostOriginFormSet(self.request.POST, self.request.FILES)
        else:
            context['origin_formset'] = PostOriginFormSet()
        return context

    def form_valid(self, form):
        """
        Сохраняет пост и связанный формсет.

        Аргументы:
            form: Форма поста.

        Возвращает:
            HttpResponse: Перенаправление.
        """
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
        """
        Обрабатывает ошибки формы.

        Аргументы:
            form: Форма с ошибками.

        Возвращает:
            HttpResponse: Ошибка.
        """
        return super().form_invalid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Обновляет существующий пост.

    Атрибуты:
        model: Модель Post.
        template_name: Шаблон для формы.
        form_class: Форма для редактирования.
        success_url: URL после успешного обновления.
    """
    model = Post
    template_name = 'posts/post_update.html'
    form_class = PostForm
    success_url = reverse_lazy('posts:post_list')

    def get_form(self, form_class=None):
        """
        Ограничивает поля формы для обычных пользователей.

        Аргументы:
            form_class: Класс формы.

        Возвращает:
            Form: Настроенная форма.
        """
        form = super().get_form(form_class)
        if not self.request.user.has_perm('posts.change_post'):
            for field in ['is_active', 'author', 'views']:
                if field in form.fields:
                    del form.fields[field]
        return form

    def get_context_data(self, **kwargs):
        """
        Добавляет формсет для происхождения.

        Аргументы:
            **kwargs: Дополнительные аргументы.

        Возвращает:
            dict: Контекст для шаблона.
        """
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['origin_formset'] = PostOriginFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            context['origin_formset'] = PostOriginFormSet(instance=self.object)
        return context

    def test_func(self):
        """
        Проверяет права доступа.

        Возвращает:
            bool: Разрешён ли доступ.
        """
        post = self.get_object()
        if self.request.user.has_perm('posts.change_post'):
            return True
        return post.author == self.request.user

    def handle_no_permission(self):
        """
        Обрабатывает отсутствие прав.

        Возвращает:
            HttpResponse: Перенаправление.
        """
        return redirect('posts:post_list')

    def form_valid(self, form):
        """
        Сохраняет обновлённый пост и формсет.

        Аргументы:
            form: Форма поста.

        Возвращает:
            HttpResponse: Перенаправление.
        """
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
        """
        Обрабатывает ошибки формы.

        Аргументы:
            form: Форма с ошибками.

        Возвращает:
            HttpResponse: Ошибка.
        """
        return super().form_invalid(form)

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Удаляет пост.

    Атрибуты:
        model: Модель Post.
        template_name: Шаблон для подтверждения.
        success_url: URL после удаления.
    """
    model = Post
    template_name = 'posts/post_delete.html'
    success_url = reverse_lazy('posts:post_list')

    def test_func(self):
        """
        Проверяет права на удаление.

        Возвращает:
            bool: Разрешён ли доступ.
        """
        post = self.get_object()
        if self.request.user.has_perm('posts.delete_post'):
            return True
        return post.author == self.request.user

    def handle_no_permission(self):
        """
        Обрабатывает отсутствие прав.

        Возвращает:
            HttpResponse: Перенаправление.
        """
        return redirect('posts:post_list')

    def form_valid(self, form):
        """
        Подтверждает удаление.

        Аргументы:
            form: Форма удаления.

        Возвращает:
            HttpResponse: Перенаправление.
        """
        return super().form_valid(form)

class ReviewCreateView(LoginRequiredMixin, CreateView):
    """
    Создаёт новый отзыв.

    Атрибуты:
        model: Модель Review.
        form_class: Форма для отзыва.
        template_name: Шаблон для формы.
        success_url: URL после создания.
    """
    model = Review
    form_class = ReviewForm
    template_name = 'posts/review_form.html'
    success_url = reverse_lazy('posts:post_list')

    def form_valid(self, form):
        """
        Сохраняет отзыв.

        Аргументы:
            form: Форма отзыва.

        Возвращает:
            HttpResponse: Перенаправление.
        """
        form.instance.author = self.request.user
        form.instance.post_id = self.kwargs['pk']
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """
        Добавляет ID поста в контекст.

        Аргументы:
            **kwargs: Дополнительные аргументы.

        Возвращает:
            dict: Контекст для шаблона.
        """
        context = super().get_context_data(**kwargs)
        context['post_id'] = self.kwargs['pk']
        return context

class ReviewDetailView(DetailView):
    """
    Отображает детальную информацию об отзыве.

    Атрибуты:
        model: Модель Review.
        template_name: Шаблон для отображения.
        context_object_name: Имя объекта в шаблоне.
        slug_url_kwarg: Имя параметра slug в URL.
    """
    model = Review
    template_name = 'posts/review_detail.html'
    context_object_name = 'review'
    slug_url_kwarg = 'review_slug'

    def get_object(self):
        """
        Получает отзыв по slug.

        Возвращает:
            Review: Объект отзыва.
        """
        return Review.objects.get(slug=self.kwargs['review_slug'])

@permission_required('posts.change_post', raise_exception=True)
def toggle_post_active(request, pk):
    """
    Переключает статус активности поста.

    Аргументы:
        request: HTTP-запрос.
        pk: ID поста.

    Возвращает:
        HttpResponse: Перенаправление.
    """
    post = get_object_or_404(Post, pk=pk)
    post.is_active = not post.is_active
    post.save()
    return redirect('posts:post_list')