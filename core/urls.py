from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", lambda req: redirect("usuarios:login")),
    path("", include("dashboard.urls", namespace="dashboard")),
    path("usuarios/", include("usuarios.urls", namespace="usuarios")),
    path("viaturas/", include("veiculos.urls", namespace="veiculos")),
    path("fichas/", include("fichas.urls", namespace="fichas")),
    path("seguranca/", include("accesscontrol.urls", namespace="accesscontrol")),
]

handler400 = "accesscontrol.views_erros.erro_400"
handler403 = "accesscontrol.views_erros.erro_403"
handler404 = "accesscontrol.views_erros.erro_404"
handler500 = "accesscontrol.views_erros.erro_500"


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
