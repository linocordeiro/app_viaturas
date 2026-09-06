from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', lambda req: redirect('usuarios:login')),
    path('', include('dashboard.urls', namespace='dashboard')),
    path('usuarios/', include('usuarios.urls', namespace='usuarios')),
    path('viaturas/', include('veiculos.urls', namespace='veiculos')),
    path('fichas/', include('fichas.urls', namespace='fichas')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
