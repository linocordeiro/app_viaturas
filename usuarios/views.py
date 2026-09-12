from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from accesscontrol.decorators import requer_permissao
from accesscontrol.models import LogAcesso, Perfil, UsuarioPerfil
from accesscontrol.services import invalidar_cache

from .forms import LoginForm, MeuPerfilForm, MeuPerfilSenhaForm, UsuarioForm
from .models import Usuario


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bem-vindo(a), {user.get_full_name() or user.username}!")
            next_url = request.GET.get("next")
            if not next_url or not url_has_allowed_host_and_scheme(
                url=next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                next_url = "dashboard:home"
            return redirect(next_url)
        messages.error(request, "Usuário ou senha incorretos. Verifique suas credenciais.")
    else:
        form = LoginForm()

    return render(request, "usuarios/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "Sessão encerrada com sucesso.")
    return redirect("usuarios:login")


@requer_permissao("usuarios.cadastro.visualizar")
def usuario_lista(request):
    termo = request.GET.get("q", "").strip()
    usuarios = Usuario.objects.prefetch_related("perfis_atribuidos__perfil").all()

    if termo:
        usuarios = usuarios.filter(
            username__icontains=termo
        ) | usuarios.filter(
            first_name__icontains=termo
        ) | usuarios.filter(
            last_name__icontains=termo
        ) | usuarios.filter(
            matricula__icontains=termo
        ) | usuarios.filter(
            setor__icontains=termo
        )

    return render(request, "usuarios/lista.html", {
        "usuarios": usuarios,
        "termo": termo,
    })


@requer_permissao("usuarios.cadastro.criar")
def usuario_criar(request):
    if request.method == "POST":
        form = UsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Registra quem atribuiu os perfis
            for up in UsuarioPerfil.objects.filter(usuario=user):
                up.atribuido_por = request.user
                up.save(update_fields=["atribuido_por"])
            messages.success(request, f"Usuário {user.username} cadastrado com sucesso.")
            return redirect("usuarios:lista")
    else:
        form = UsuarioForm()

    return render(request, "usuarios/form.html", {
        "form": form,
        "titulo": "Novo Usuário do Sistema",
    })


@requer_permissao("usuarios.cadastro.editar")
def usuario_editar(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == "POST":
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            invalidar_cache(usuario.pk)
            messages.success(request, f"Dados do usuário {usuario.username} atualizados com sucesso.")
            return redirect("usuarios:lista")
    else:
        form = UsuarioForm(instance=usuario)

    return render(request, "usuarios/form.html", {
        "form": form,
        "usuario": usuario,
        "titulo": f"Editar Usuário: {usuario.username}",
    })


@requer_permissao("usuarios.cadastro.toggle_ativo")
def usuario_toggle_ativo(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if usuario == request.user:
        messages.error(request, "Não é permitido desativar seu próprio usuário logado.")
        return redirect("usuarios:lista")

    usuario.is_active = not usuario.is_active
    usuario.save(update_fields=["is_active"])
    status_str = "ativado" if usuario.is_active else "desativado"
    messages.success(request, f"Usuário {usuario.username} foi {status_str} com sucesso.")
    return redirect("usuarios:lista")


@requer_permissao("usuarios.perfis.atribuir")
def usuario_perfis_gerenciar(request, pk):
    """
    Tela de gerenciamento de perfis de um usuário específico.
    Permite atribuir e remover perfis com auditoria completa.
    """
    usuario = get_object_or_404(Usuario, pk=pk)
    todos_perfis = Perfil.objects.filter(ativo=True).order_by("nome")
    vinculos = UsuarioPerfil.objects.filter(usuario=usuario).select_related("perfil", "atribuido_por")

    if request.method == "POST":
        perfis_ids = request.POST.getlist("perfis")
        perfis_selecionados = Perfil.objects.filter(pk__in=perfis_ids, ativo=True)

        # Desativa perfis desmarcados (preserva histórico)
        removidos = UsuarioPerfil.objects.filter(usuario=usuario).exclude(perfil__in=perfis_selecionados)
        for vp in removidos:
            vp.ativo = False
            vp.save(update_fields=["ativo"])
            LogAcesso.objects.create(
                tipo=LogAcesso.TIPO_REMOCAO,
                usuario=usuario,
                detalhe=f"Perfil '{vp.perfil.nome}' removido por {request.user.username}",
                ip=request.META.get("REMOTE_ADDR"),
            )

        # Ativa ou cria novos vínculos
        for perfil in perfis_selecionados:
            vp, created = UsuarioPerfil.objects.update_or_create(
                usuario=usuario,
                perfil=perfil,
                defaults={"ativo": True, "atribuido_por": request.user},
            )
            if created:
                LogAcesso.objects.create(
                    tipo=LogAcesso.TIPO_ATRIBUICAO,
                    usuario=usuario,
                    detalhe=f"Perfil '{perfil.nome}' atribuído por {request.user.username}",
                    ip=request.META.get("REMOTE_ADDR"),
                )

        invalidar_cache(usuario.pk)
        messages.success(request, f"Perfis do usuário {usuario.username} atualizados com sucesso.")
        return redirect("usuarios:lista")

    perfis_ativos_ids = set(
        vinculos.filter(ativo=True).values_list("perfil_id", flat=True)
    )

    return render(request, "usuarios/perfis.html", {
        "usuario": usuario,
        "todos_perfis": todos_perfis,
        "vinculos": vinculos,
        "perfis_ativos_ids": perfis_ativos_ids,
    })


@login_required
def meu_perfil(request):
    """Permite ao usuário editar seus próprios dados e senha."""
    if request.method == "POST":
        if "btn_dados" in request.POST:
            form_dados = MeuPerfilForm(request.POST, instance=request.user)
            form_senha = MeuPerfilSenhaForm(request.user)
            if form_dados.is_valid():
                form_dados.save()
                messages.success(request, "Seus dados foram atualizados com sucesso.")
                return redirect("usuarios:meu_perfil")
        elif "btn_senha" in request.POST:
            form_dados = MeuPerfilForm(instance=request.user)
            form_senha = MeuPerfilSenhaForm(request.user, request.POST)
            if form_senha.is_valid():
                user = form_senha.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Sua senha foi alterada com sucesso.")
                return redirect("usuarios:meu_perfil")
    else:
        form_dados = MeuPerfilForm(instance=request.user)
        form_senha = MeuPerfilSenhaForm(request.user)

    # Buscar perfis para exibição simples (se desejado) ou podemos apenas passar
    vinculos = UsuarioPerfil.objects.filter(
        usuario=request.user, ativo=True
    ).select_related("perfil")

    return render(request, "usuarios/meu_perfil.html", {
        "form_dados": form_dados,
        "form_senha": form_senha,
        "vinculos": vinculos,
    })
