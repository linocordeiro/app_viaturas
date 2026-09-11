from django.urls import path

from . import views

app_name = "usuarios"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("", views.usuario_lista, name="lista"),
    path("novo/", views.usuario_criar, name="criar"),
    path("<int:pk>/editar/", views.usuario_editar, name="editar"),
    path("<int:pk>/toggle-ativo/", views.usuario_toggle_ativo, name="toggle_ativo"),
]
