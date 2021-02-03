from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy


def register(request):
    template_name = 'users/register.html'
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created!, You are now able to log in')
            new_user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'],
            )
            login(request, new_user)
            return redirect(reverse_lazy('blog:home'))
    else:
        form = UserRegisterForm()

    context = {'form': form}
    return render(request, template_name, context)

@login_required
def profile(request):
    template_name = 'users/profile.html'

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    
    return render(request, template_name, context)