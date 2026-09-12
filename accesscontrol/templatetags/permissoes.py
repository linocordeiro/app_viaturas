"""
Template tags de controle de permissão.

Uso nos templates:
    {% load permissoes %}

    {% tem_perm "operacao_diaria.fichas.exportar_pdf" as pode_exportar %}
    {% if pode_exportar %}
      <a href="...">Exportar PDF</a>
    {% endif %}
"""

from django import template

from accesscontrol.services import tem_permissao

register = template.Library()


@register.simple_tag(takes_context=True)
def tem_perm(context, codigo: str) -> bool:
    """
    Verifica se o usuário da requisição possui a permissão indicada.
    Retorna True/False para uso em {% if %} após atribuição com 'as'.
    """
    request = context.get("request")
    if request is None:
        return False
    return tem_permissao(request.user, codigo)
