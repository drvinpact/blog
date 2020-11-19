from django.urls import reverse
from django.shortcuts import render

def error_404(request, exception):
    template_name = 'errors/error.html'
    context = {
        'error': 404,
        'title': "Page Not Found",
        'subtitle': "UH OH! You're lost.",
        'message': "The page you are looking for does not exist. How you got here is a mystery.",
        'submessage': "But you can click the button below to go back to the homepage.",
        'button': "Back Home",
        'url': reverse('blog:home')
    }
    return render(request, template_name, context, status=404)

def error_500(request, exception=None):
    template_name = 'errors/error.html'
    context = {
        'error': 500,
        'title': "Internal Server Error",
        'subtitle': "Oops! Something went wrong.",
        'message': "It's broken, but it´s not your fault.",
        'submessage': "But you can click the button below to go back to the homepage.",
        'button': "Back Home",
        'url': reverse('blog:home')
    }
    return render(request, template_name, context, status=500)

def error_403(request, exception=None):
    template_name = 'errors/error.html'
    context = {
        'error': 403,
        'title': "Access Denied",
        'subtitle': "Ah Ah Ah! You didn't say the magic word.",
        'message': "You don't have permission to access this area.",
        'submessage': "But you can click the button below to go back to the homepage.",
        'button': "Back Home",
        'url': reverse('blog:home')
    }
    return render(request, template_name, context, status=403)

def error_400(request, exception=None):
    template_name = 'errors/error.html'
    context = {
        'error': 400,
        'title': "Bad Request",
        'subtitle': "Oops! There's nothing here.",
        'message': "The page you have requested cannot be found.",
        'submessage': "But you can click the button below to go back to the homepage.",
        'button': "Back Home",
        'url': reverse('blog:home')
    }
    return render(request, template_name, context, status=400)
