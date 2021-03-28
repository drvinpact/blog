from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls import handler404, handler500
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from users import views as user_views
from errors.views import error_400, error_403, error_404, error_500

handler400 = error_400
handler403 = error_403
handler404 = error_404
handler500 = error_500

urlpatterns = [
    path('admin/', admin.site.urls),    
    path('register/', user_views.register, name='register'),
    path('profile/', user_views.profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('password-reset/', 
        auth_views.PasswordResetView.as_view(
            template_name='users/password_reset.html'
        ), 
        name='password_reset'),
    path('password-reset/done/', 
        auth_views.PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'
        ), 
        name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html'
        ), 
        name='password_reset_confirm'),
    path('password-reset-complete/', 
        auth_views.PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'
        ), 
        name='password_reset_complete'),

    path('', include(('blog.urls', 'blog'), namespace="blog")),
    path('messenger/', include(('messenger.urls', 'messenger'), namespace="messenger")),
    path('notifications/', include(('notifications.urls', 'notifications'), namespace="notifications")),

    path('summernote/', include('django_summernote.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)