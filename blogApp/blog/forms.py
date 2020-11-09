from django import forms

class CommentForm(forms.Form):
    parent_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    content = forms.CharField(label='', widget=forms.Textarea(attrs={
        'rows': 4,
        'cols': 100
    }))

class ReplyForm(forms.Form):
    parent_id = forms.CharField(widget=forms.HiddenInput())
    content = forms.CharField(label='', widget=forms.Textarea(attrs={
        'rows': 4,
        'cols': 100
    }))