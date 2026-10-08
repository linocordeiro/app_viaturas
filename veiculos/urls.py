from django.urls import path

from . import views

app_name = "veiculos"

urlpatterns = [
    path("", views.viatura_lista, name="lista"),
    path("nova/", views.viatura_criar, name="criar"),
    path("<int:pk>/", views.viatura_detalhe, name="detalhe"),
    path("<int:pk>/editar/", views.viatura_editar, name="editar"),
    path("<int:viatura_pk>/manutencao/nova/", views.manutencao_criar, name="manutencao_criar"),
    path("manutencoes/", views.manutencao_lista, name="lista_manutencoes"),
    path("exportar/pdf/", views.exportar_viaturas_pdf, name="exportar_pdf"),
    path("exportar/excel/", views.exportar_viaturas_excel, name="exportar_excel"),
    path("<int:pk>/manutencoes/pdf/", views.exportar_manutencoes_pdf, name="exportar_manutencoes_pdf"),
    path("<int:pk>/manutencoes/excel/", views.exportar_manutencoes_excel, name="exportar_manutencoes_excel"),

    # Gestão de Classificação pelo NUTRAN
    path("classificacao/", views.classificacao_lista, name="classificacao_lista"),
    path("classificacao/<int:pk>/", views.classificacao_definir, name="classificacao_definir"),

    # Configuração de Integração de Placas (Administração)
    path("configuracao/consulta-placa/", views.configuracao_placa_view, name="configuracao_placa"),
    path("configuracao/consulta-placa/testar/", views.configuracao_placa_testar, name="configuracao_placa_testar"),
]
