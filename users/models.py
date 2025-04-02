from django.db import models

class User(models.Model):
    username = models.CharField(max_length=150, unique=True, verbose_name="Имя пользователя")
    email = models.EmailField(unique=True, verbose_name="Email")
    first_name = models.CharField(max_length=100, blank=True, verbose_name="Имя")
    last_name = models.CharField(max_length=100, blank=True, verbose_name="Фамилия")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"