from django.urls import path

from . import views

app_name = "fichas"

urlpatterns = [
    path("", views.ficha_lista, name="lista"),
    path("hoje/", views.ficha_hoje, name="hoje"),
    path("nova/", views.ficha_criar, name="criar"),
    path("<int:pk>/", views.ficha_detalhe, name="detalhe"),
    path("<int:ficha_pk>/saida/", views.registro_saida_criar, name="saida_criar"),
    path("registro/<int:pk>/chegada/", views.registro_chegada_concluir, name="chegada_concluir"),
    path("registro/<int:pk>/editar/", views.registro_editar, name="registro_editar"),
    path("<int:pk>/assinar/responsavel/", views.ficha_assinar_responsavel, name="assinar_responsavel"),
    path("<int:pk>/assinar/chefia/", views.ficha_assinar_chefia, name="assinar_chefia"),
    path("<int:pk>/encerrar/", views.ficha_encerrar, name="encerrar"),
    path("<int:pk>/pdf/", views.exportar_ficha_pdf, name="exportar_pdf"),
    path("<int:pk>/excel/", views.exportar_ficha_excel, name="exportar_excel"),
]
