"""
Rotas para o módulo de controle de acesso e auditoria.
"""

from django.urls import path
from . import views_auditoria

app_name = "accesscontrol"

urlpatterns = [
    path("auditoria/", views_auditoria.auditoria_lista, name="auditoria_lista"),
    path("auditoria/<int:pk>/detalhes/", views_auditoria.auditoria_detalhes_json, name="auditoria_detalhes_json"),
]
