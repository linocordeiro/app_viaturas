from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import LoginForm, UsuarioForm
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


@login_required
def usuario_lista(request):
    termo = request.GET.get("q", "").strip()
    usuarios = Usuario.objects.all()

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


@login_required
def usuario_criar(request):
    if request.method == "POST":
        form = UsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Usuário {user.username} cadastrado com sucesso.")
            return redirect("usuarios:lista")
    else:
        form = UsuarioForm()

    return render(request, "usuarios/form.html", {
        "form": form,
        "titulo": "Novo Usuário do Sistema",
    })


@login_required
def usuario_editar(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == "POST":
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f"Dados do usuário {usuario.username} atualizados com sucesso.")
            return redirect("usuarios:lista")
    else:
        form = UsuarioForm(instance=usuario)

    return render(request, "usuarios/form.html", {
        "form": form,
        "usuario": usuario,
        "titulo": f"Editar Usuário: {usuario.username}",
    })


@login_required
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


@login_required
def usuario_resetar_senha(request, pk):
    if not getattr(request.user, "is_admin_user", False):
        messages.error(request, "Permissão negada. Apenas administradores podem redefinir senhas.")
        return redirect("usuarios:lista")

    usuario = get_object_or_404(Usuario, pk=pk)
    usuario.set_password("mudar@123")
    usuario.save()

    nome_exibicao = usuario.get_full_name() or usuario.username
    messages.success(
        request,
        f"A senha do usuário '{usuario.username}' ({nome_exibicao}) foi resetada com sucesso para a senha padrão 'mudar@123'."
    )
    return redirect("usuarios:lista")

