from django import forms
from django.forms import ModelForm
from .models import Post
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'image', 'category', 'content', 'tags', 'is_active']
        labels = {
            'title': 'Título',
            'image': 'Imagen',
            'category': 'Categoría',
            'content': 'Contenido',
            'tags': 'Etiquetas',
            'is_active': 'Activo'
        }
        widgets = {
            'content': SummernoteWidget(),
        }

class CommentForm(forms.Form):
    parent_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    name = forms.CharField(label='Name*', max_length=255, required=False)
    email = forms.EmailField(label='Email*', max_length=255, required=False)
    website = forms.CharField(max_length=255, required=False)
    content = forms.CharField(label='Message', widget=forms.Textarea(attrs={
        'rows': 4,
        'cols': 100
    }))

class ReplyForm(forms.Form):
    parent_id = forms.CharField(widget=forms.HiddenInput())
    content = forms.CharField(label='', widget=forms.Textarea(attrs={
        'rows': 4,
        'cols': 100
    }))