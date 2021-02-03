from django.urls import reverse
from django.shortcuts import render

def error_404(request, exception):
    template_name = 'errors/error.html'
    context = {
        'error': 404,
        'title': "La página buscada no existe",
        'subtitle': "¡JO! Estás perdido...",
        'message': "La página que buscas no existe. Cómo has llegado aquí es todo un misterio.",
        'submessage': "Pero tranquilo, si pinchas abajo puedes volver a tierra firme.",
        'button': "Volver",
        'url': reverse('blog:home')
    }
    return render(request, template_name, context, status=404)

def error_500(request, exception=None):
    template_name = 'errors/error.html'
    context = {
        'error': 500,
        'title': "Error en el servidor",
        'subtitle': "¡Ups! Algo no anda nada bien.",
        'message': "Se ha estropeado, pero no es tu culpa.",
        'submessage': "Tranquilo, si pinchas abajo puedes volver a tierra firme.",
        'button': "Volver",
        'url': reverse('blog:home')
    }
    return render(request, template_name, context, status=500)

def error_403(request, exception=None):
    template_name = 'errors/error.html'
    context = {
        'error': 403,
        'title': "Acceso denegado",
        'subtitle': "¡Ah ah ah! No dijiste la palabra mágica.",
        'message': "No tienes los permisos suficientes para estar aquí.",
        'submessage': "Si pinchas abajo puedes volver a tierra firme.",
        'button': "Volver",
        'url': reverse('blog:home')
    }
    return render(request, template_name, context, status=403)

def error_400(request, exception=None):
    template_name = 'errors/error.html'
    context = {
        'error': 400,
        'title': "Recurso no encontrado",
        'subtitle': "¡Ups! Aquí no hay nada.",
        'message': "Lo que buscas no se encuentra disponible.",
        'submessage': "Pero tranquilo, si pinchas abajo puedes volver a tierra firme.",
        'button': "Volver",
        'url': reverse('blog:home')
    }
    return render(request, template_name, context, status=400)
