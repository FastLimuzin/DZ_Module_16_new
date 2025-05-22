from django import forms
from django.forms import inlineformset_factory
from .models import Post, Origin
from django import forms
from .models import Post, Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'rating', 'slug']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4}),
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)]),
            'slug': forms.HiddenInput(),
        }

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image', 'is_active']
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