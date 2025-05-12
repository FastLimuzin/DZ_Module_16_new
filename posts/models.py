from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils.crypto import get_random_string
import datetime
from django.utils.translation import gettext_lazy as _

def validate_creation_date(value):
    if value > datetime.datetime.now().replace(tzinfo=None):
        raise ValidationError(_('Дата создания не может быть в будущем!'))

def generate_unique_slug(model_instance, base_slug=None):
    if not base_slug:
        base_slug = get_random_string(length=8)  # Случайная строка длиной 8 символов
    slug = base_slug
    counter = 1
    while model_instance.__class__.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug

class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание")
    image = models.ImageField(upload_to='posts/images/', blank=True, null=True, verbose_name="Изображение")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name="Автор", null=True)
    created_at = models.DateTimeField(auto_now_add=True, validators=[validate_creation_date], verbose_name="Дата создания")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    views = models.PositiveIntegerField(default=0, verbose_name="Просмотры")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name="Пост")
    text = models.TextField(verbose_name="Текст комментария")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Комментарий к {self.post.title}"

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

class Origin(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='origins', verbose_name="Персонаж (Пост)")
    parent_name = models.CharField(max_length=100, verbose_name="Имя родителя")
    origin = models.CharField(max_length=200, verbose_name="Место происхождения", help_text="Например, Асгард, Земля")
    description = models.TextField(blank=True, verbose_name="Описание")

    def __str__(self):
        return f"Происхождение для {self.post.title}: {self.parent_name}"

    class Meta:
        verbose_name = "Происхождение"
        verbose_name_plural = "Происхождения"

class Review(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reviews', verbose_name="Пост")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор отзыва")
    text = models.TextField(verbose_name="Текст отзыва")
    rating = models.PositiveSmallIntegerField(verbose_name="Оценка", choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    slug = models.SlugField(max_length=50, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Отзыв к {self.post.title} от {self.author.username} (slug: {self.slug})"

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"