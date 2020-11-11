from django import forms

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