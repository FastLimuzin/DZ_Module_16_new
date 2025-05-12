from django import forms
from django.forms import inlineformset_factory
from .models import Post, Origin

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image']
        labels = {
            'title': 'Заголовок',
            'content': 'Содержание',
            'image': 'Изображение',
        }

PostOriginFormSet = inlineformset_factory(
    Post,
    Origin,
    fields=('parent_name', 'origin', 'description'),
    extra=1,
    can_delete=True,
)