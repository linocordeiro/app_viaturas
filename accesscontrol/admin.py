from django.contrib import admin

from .models import Acao, DashboardWidget, LogAcesso, Modulo, Perfil, Submodulo, UsuarioPerfil


@admin.register(Modulo)
class ModuloAdmin(admin.ModelAdmin):
    list_display = ("nome", "codigo", "ordem", "ativo")
    list_editable = ("ordem", "ativo")
    prepopulated_fields = {"codigo": ("nome",)}


@admin.register(Submodulo)
class SubmoduloAdmin(admin.ModelAdmin):
    list_display = ("nome", "modulo", "codigo", "ordem", "ativo")
    list_filter = ("modulo",)
    list_editable = ("ordem", "ativo")


@admin.register(Acao)
class AcaoAdmin(admin.ModelAdmin):
    list_display = ("codigo_completo", "nome", "tipo", "modulo", "submodulo", "ativo")
    list_filter = ("modulo", "tipo", "ativo")
    readonly_fields = ("codigo_completo",)
    search_fields = ("codigo_completo", "nome")


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("nome", "ativo", "total_acoes")
    filter_horizontal = ("acoes",)

    @admin.display(description="Ações")
    def total_acoes(self, obj):
        return obj.acoes.count()


class UsuarioPerfilInline(admin.TabularInline):
    model = UsuarioPerfil
    extra = 1
    readonly_fields = ("atribuido_em",)
    autocomplete_fields = ("perfil",)


@admin.register(UsuarioPerfil)
class UsuarioPerfilAdmin(admin.ModelAdmin):
    list_display = ("usuario", "perfil", "ativo", "atribuido_por", "atribuido_em")
    list_filter = ("ativo", "perfil")
    readonly_fields = ("atribuido_em",)
    search_fields = ("usuario__username", "perfil__nome")


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ("nome", "codigo", "ordem", "ativo")
    filter_horizontal = ("perfis",)


@admin.register(LogAcesso)
class LogAcessoAdmin(admin.ModelAdmin):
    list_display = ("tipo", "usuario", "acao_tentada", "rota", "ip", "registrado_em")
    list_filter = ("tipo",)
    readonly_fields = ("tipo", "usuario", "acao_tentada", "rota", "ip", "detalhe", "registrado_em")
    search_fields = ("usuario__username", "acao_tentada", "rota")

    def has_add_permission(self, request):
        return False  # Log é imutável — ninguém insere manualmente

    def has_change_permission(self, request, obj=None):
        return False  # Log é imutável
