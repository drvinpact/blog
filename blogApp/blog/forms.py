from django import forms

class CommentForm(forms.Form):
    content = forms.CharField(label='', widget=forms.Textarea(attrs={
        'rows': 4,
        'cols': 100
    }))