from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth.forms import UserCreationForm


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserUpdateForm(ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']    

class ProfileUpdateForm(ModelForm):
    is_public = forms.BooleanField(label='Public', required=False)
    
    class Meta:
        model = Profile
        fields = ['bio', 'image', 'is_public']