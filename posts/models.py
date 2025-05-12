from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import datetime
from django.utils.translation import gettext_lazy as _

def validate_creation_date(value):
    if value > datetime.now().replace(tzinfo=None):
        raise ValidationError(_('Дата создания не может быть в будущем!'))

class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание")
    image = models.ImageField(upload_to='posts/images/', blank=True, null=True, verbose_name="Изображение")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name="Автор", null=True)
    created_at = models.DateTimeField(auto_now_add=True, validators=[validate_creation_date], verbose_name="Дата создания")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    views = models.PositiveIntegerField(default=0, verbose_name="Просмотры")  # Новое поле для счётчика

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