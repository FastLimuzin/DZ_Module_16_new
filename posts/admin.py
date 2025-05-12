from django.contrib import admin
from .models import Post, Comment, Origin

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'id')
    list_filter = ('author', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'title': ('content',)}
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    fields = ('title', 'content', 'image', 'author')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'text', 'created_at', 'id')
    list_filter = ('post', 'created_at')
    search_fields = ('text',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    fields = ('post', 'text')

@admin.register(Origin)
class OriginAdmin(admin.ModelAdmin):
    list_display = ('post', 'parent_name', 'origin', 'id')
    list_filter = ('post',)
    search_fields = ('parent_name', 'origin', 'description')
    ordering = ('post',)
    fields = ('post', 'parent_name', 'origin', 'description')