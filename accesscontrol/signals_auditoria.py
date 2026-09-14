"""
Signals para auditoria automatizada do sistema.
Captura eventos de autenticação e alterações em modelos críticos.
"""

from django.contrib.auth import user_logged_in, user_login_failed, user_logged_out
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .audit_service import registrar_log
from .models import CodigoAcao


# ── 1. Autenticação ──────────────────────────────────────────────────────────


@receiver(user_logged_in)
def on_user_logged_in(sender, request, user, **kwargs):
    registrar_log(
        codigo=CodigoAcao.AUTH_LOGIN,
        descricao=f"Login realizado com sucesso por {user.get_full_name() or user.username}",
        usuario=user,
        detalhes={"username": user.username, "matricula": getattr(user, "matricula", "")},
    )


@receiver(user_logged_out)
def on_user_logged_out(sender, request, user, **kwargs):
    if user:
        registrar_log(
            codigo=CodigoAcao.AUTH_LOGOUT,
            descricao=f"Sessão encerrada por {user.get_full_name() or user.username}",
            usuario=user,
            detalhes={"username": user.username},
        )


@receiver(user_login_failed)
def on_user_login_failed(sender, credentials, request, **kwargs):
    username = credentials.get("username", "desconhecido")
    registrar_log(
        codigo=CodigoAcao.AUTH_FALHA,
        descricao=f"Tentativa de login inválida para o usuário '{username}'",
        detalhes={"username_tentado": username},
    )


# ── 2. Gestão de Frota (Viaturas e Manutenções) ──────────────────────────────


@receiver(post_save, sender="veiculos.Viatura")
def on_viatura_save(sender, instance, created, **kwargs):
    if created:
        codigo = CodigoAcao.VIAT_CRIADA
        desc = f"Cadastro da viatura {instance.marca} {instance.modelo} (Placa {instance.placa})"
    elif not instance.ativo:
        codigo = CodigoAcao.VIAT_DESATIVADA
        desc = f"Desativação da viatura {instance.placa} da frota"
    else:
        codigo = CodigoAcao.VIAT_EDITADA
        desc = f"Atualização cadastral da viatura {instance.placa}"

    registrar_log(
        codigo=codigo,
        descricao=desc,
        objeto_repr=f"Viatura {instance.placa} ({instance.marca} {instance.modelo})",
        objeto_id=str(instance.pk),
        tabela_afetada="veiculos.Viatura",
        detalhes={
            "placa": instance.placa,
            "modelo": instance.modelo,
            "marca": instance.marca,
            "status": instance.status,
            "km_atual": instance.km_atual,
            "ativo": instance.ativo,
        },
    )


@receiver(post_save, sender="veiculos.Manutencao")
def on_manutencao_save(sender, instance, created, **kwargs):
    codigo = CodigoAcao.MANUT_REGISTRADA if created else CodigoAcao.MANUT_EDITADA
    placa = getattr(instance.viatura, "placa", "N/A")
    tipo = getattr(instance, "get_tipo_display", lambda: instance.tipo)()
    desc = f"Registro de manutenção ({tipo}) para a viatura {placa}" if created else f"Atualização de manutenção ({tipo}) da viatura {placa}"

    registrar_log(
        codigo=codigo,
        descricao=desc,
        objeto_repr=f"Manutenção {tipo} - Viatura {placa}",
        objeto_id=str(instance.pk),
        tabela_afetada="veiculos.Manutencao",
        detalhes={
            "viatura_placa": placa,
            "tipo": instance.tipo,
            "status": getattr(instance, "status", ""),
            "km_no_momento": getattr(instance, "km_no_momento", 0),
            "custo": str(getattr(instance, "custo", "0")),
        },
    )


# ── 3. Operação Diária (Fichas e Registros de Uso) ───────────────────────────


@receiver(post_save, sender="fichas.FichaControle")
def on_ficha_save(sender, instance, created, **kwargs):
    data_formatada = instance.data_expediente.strftime("%d/%m/%Y") if instance.data_expediente else "N/A"
    if created:
        codigo = CodigoAcao.FICH_ABERTA
        desc = f"Abertura da ficha de controle nº {instance.pk} ({data_formatada})"
    elif instance.status == "ENCERRADA":
        codigo = CodigoAcao.FICH_ENCERRADA
        desc = f"Encerramento da ficha de controle nº {instance.pk} ({data_formatada})"
    else:
        codigo = CodigoAcao.FICH_EDITADA
        desc = f"Edição dos dados da ficha de controle nº {instance.pk} ({data_formatada})"

    registrar_log(
        codigo=codigo,
        descricao=desc,
        objeto_repr=f"Ficha de Controle #{instance.pk} ({data_formatada})",
        objeto_id=str(instance.pk),
        tabela_afetada="fichas.FichaControle",
        detalhes={
            "id": instance.pk,
            "data_expediente": str(instance.data_expediente),
            "status": instance.status,
            "vigilante": str(instance.nome_vigilante or ""),
            "visto_responsavel": instance.visto_responsavel,
            "visto_chefia": instance.visto_chefia,
        },
    )



@receiver(post_save, sender="fichas.RegistroUso")
def on_registro_uso_save(sender, instance, created, **kwargs):
    placa = getattr(instance.viatura, "placa", "N/A")
    ficha_id = getattr(instance.ficha, "pk", "N/A")
    condutor = str(getattr(instance, "condutor_nome", "") or getattr(instance, "condutor", ""))

    if created:
        codigo = CodigoAcao.FICH_SAIDA_REGISTRADA
        desc = f"Registro de saída da viatura {placa} (Ficha #{ficha_id}, Condutor: {condutor})"
    elif instance.horario_retorno:
        codigo = CodigoAcao.FICH_RETORNO_REGISTRADO
        desc = f"Registro de retorno da viatura {placa} (Ficha #{ficha_id})"
    else:
        codigo = CodigoAcao.FICH_MOVIMENTACAO_EDITADA
        desc = f"Atualização do registro de movimentação da viatura {placa} (Ficha #{ficha_id})"

    registrar_log(
        codigo=codigo,
        descricao=desc,
        objeto_repr=f"Movimentação Viatura {placa} (Ficha #{ficha_id})",
        objeto_id=str(instance.pk),
        tabela_afetada="fichas.RegistroUso",
        detalhes={
            "viatura": placa,
            "ficha_id": ficha_id,
            "condutor": condutor,
            "km_saida": instance.km_saida,
            "km_retorno": instance.km_retorno,
            "horario_saida": str(instance.horario_saida or ""),
            "horario_retorno": str(instance.horario_retorno or ""),
            "destino": getattr(instance, "destino", ""),
        },
    )


# ── 4. Gestão de Usuários e Perfis ───────────────────────────────────────────


@receiver(post_save, sender="usuarios.Usuario")
def on_usuario_save(sender, instance, created, **kwargs):
    # Evita gravar log durante migrações ou testes se não for usuário real
    if created:
        codigo = CodigoAcao.USER_CRIADO
        desc = f"Cadastro do usuário {instance.username} ({instance.get_full_name() or 'Sem nome'})"
    elif not instance.is_active:
        codigo = CodigoAcao.SEC_USUARIO_DESATIVADO
        desc = f"Desativação de acesso do usuário {instance.username}"
    else:
        codigo = CodigoAcao.USER_EDITADO
        desc = f"Atualização cadastral do usuário {instance.username}"

    registrar_log(
        codigo=codigo,
        descricao=desc,
        objeto_repr=f"Usuário {instance.username}",
        objeto_id=str(instance.pk),
        tabela_afetada="usuarios.Usuario",
        detalhes={
            "username": instance.username,
            "nome": instance.get_full_name(),
            "matricula": getattr(instance, "matricula", ""),
            "setor": getattr(instance, "setor", ""),
            "is_active": instance.is_active,
        },
    )


@receiver(post_save, sender="accesscontrol.UsuarioPerfil")
def on_usuario_perfil_save_audit(sender, instance, created, **kwargs):
    if created:
        registrar_log(
            codigo=CodigoAcao.SEC_PERFIL_ATRIBUIDO,
            descricao=f"Atribuição do perfil '{instance.perfil.nome}' para o usuário {instance.usuario.username}",
            objeto_repr=f"{instance.usuario.username} -> {instance.perfil.nome}",
            objeto_id=str(instance.pk),
            tabela_afetada="accesscontrol.UsuarioPerfil",
            detalhes={
                "usuario": instance.usuario.username,
                "perfil": instance.perfil.nome,
                "atribuido_por": str(instance.atribuido_por or ""),
            },
        )


@receiver(post_delete, sender="accesscontrol.UsuarioPerfil")
def on_usuario_perfil_delete_audit(sender, instance, **kwargs):
    usuario_nome = getattr(instance.usuario, "username", "Usuário")
    perfil_nome = getattr(instance.perfil, "nome", "Perfil")
    registrar_log(
        codigo=CodigoAcao.SEC_PERFIL_REMOVIDO,
        descricao=f"Remoção do perfil '{perfil_nome}' do usuário {usuario_nome}",
        objeto_repr=f"{usuario_nome} -/-> {perfil_nome}",
        objeto_id=str(instance.pk),
        tabela_afetada="accesscontrol.UsuarioPerfil",
        detalhes={"usuario": usuario_nome, "perfil": perfil_nome},
    )
