from datetime import timedelta
import os
import re
from typing import Optional

from django.utils import timezone

from .base import ResultadoConsulta
from .provedor_gratuito import ProvedorGratuito
from .provedor_serpro import ProvedorSerpro

REGEX_PLACA_MERCOSUL = re.compile(r"^[A-Z]{3}[0-9][A-Z][0-9]{2}$")
REGEX_PLACA_ANTIGA = re.compile(r"^[A-Z]{3}[0-9]{4}$")


def normalizar_placa(placa: str) -> str:
    """
    Remove traços, pontos e espaços, retornando a placa em maiúsculas com 7 caracteres.
    Ex: 'ABC-1234' -> 'ABC1234', 'BRA-2E19' -> 'BRA2E19'.
    """
    if not placa:
        return ""
    return re.sub(r"[^A-Za-z0-9]", "", placa).upper().strip()


def validar_formato_placa(placa: str) -> bool:
    """Verifica se a placa normalizada possui formato Mercosul ou antigo válido."""
    placa_limpa = normalizar_placa(placa)
    return bool(REGEX_PLACA_MERCOSUL.match(placa_limpa) or REGEX_PLACA_ANTIGA.match(placa_limpa))


class OrquestradorConsultaPlaca:
    def __init__(self):
        self.provedor_gratuito = ProvedorGratuito()
        self.provedor_serpro = ProvedorSerpro()

    def _obter_proxy(self, config) -> str:
        # Prioridade 1: Configuração salva no banco de dados
        proxy_banco = getattr(config, "proxy_url", "").strip()
        if proxy_banco:
            return proxy_banco

        # Prioridade 2: Variável de ambiente institucional
        return os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY") or ""

    def consultar(self, placa_raw: str, forcar_api: bool = False) -> ResultadoConsulta:
        from veiculos.models import ConfiguracaoConsultaPlaca, PlacaConsultada, Viatura

        placa = normalizar_placa(placa_raw)
        if not placa or not validar_formato_placa(placa):
            return ResultadoConsulta(
                sucesso=False,
                placa=placa,
                origem="MANUAL",
                mensagem="Formato de placa inválido. Use o padrão Mercosul (ex: BRA2E19) ou tradicional (ex: ABC1234).",
            )

        config = ConfiguracaoConsultaPlaca.obter_configuracao()

        # 1. Se a viatura já estiver cadastrada na base local (frota ou histórico)
        viatura_existente = Viatura.objects.filter(placa=placa).first()
        if viatura_existente and not forcar_api:
            origem = "FROTA" if viatura_existente.eh_frota else "CACHE"
            return ResultadoConsulta(
                sucesso=True,
                placa=placa,
                marca=viatura_existente.marca,
                modelo=viatura_existente.modelo,
                cor=viatura_existente.cor,
                ano=str(viatura_existente.ano_modelo or viatura_existente.ano_fabricacao or ""),
                origem=origem,
                provedor="Frota / Base Local",
                mensagem=f"Veículo localizado na base interna ({viatura_existente.get_classificacao_display()}).",
            )

        # 2. Se a consulta externa estiver desabilitada pelo administrador
        if not config.consulta_habilitada:
            return ResultadoConsulta(
                sucesso=False,
                placa=placa,
                origem="MANUAL",
                provedor="Nenhum",
                mensagem="Consulta externa desabilitada no painel. Preencha marca e modelo manualmente.",
            )

        # 3. Consulta ao cache local de placas consultadas anteriormente
        if not forcar_api:
            limite_cache = timezone.now() - timedelta(days=config.cache_dias)
            cache = PlacaConsultada.objects.filter(placa=placa, consultado_em__gte=limite_cache).first()
            if cache:
                return ResultadoConsulta(
                    sucesso=True,
                    placa=placa,
                    marca=cache.marca,
                    modelo=cache.modelo,
                    cor=cache.cor,
                    ano=cache.ano,
                    origem="CACHE",
                    provedor=f"{cache.provedor} (Cache)",
                    mensagem="Veículo identificado a partir do histórico local (cache).",
                )

        # 4. Verificação do Circuit Breaker (se houveram falhas consecutivas recentes)
        agora = timezone.now()
        if config.circuito_aberto_ate and config.circuito_aberto_ate > agora:
            minutos_restantes = max(1, int((config.circuito_aberto_ate - agora).total_seconds() / 60))
            return ResultadoConsulta(
                sucesso=False,
                placa=placa,
                origem="MANUAL",
                provedor="Circuito Aberto",
                mensagem=f"Provedor externo em pausa de contingência ({minutos_restantes} min restantes). Modo manual ativado.",
            )

        # 5. Execução da chamada via provedor ativo
        proxy_url = self._obter_proxy(config)
        provedor = self.provedor_serpro if config.provedor_ativo == config.PROVEDOR_SERPRO else self.provedor_gratuito
        resultado = provedor.consultar(placa, config, proxy_url=proxy_url)

        # 6. Atualização de estado da integração
        if resultado.sucesso:
            config.falhas_consecutivas = 0
            config.circuito_aberto_ate = None
            config.ultimo_sucesso = agora
            config.save(update_fields=["falhas_consecutivas", "circuito_aberto_ate", "ultimo_sucesso", "atualizado_em"])

            # Alimenta o cache local
            PlacaConsultada.objects.update_or_create(
                placa=placa,
                defaults={
                    "marca": resultado.marca,
                    "modelo": resultado.modelo,
                    "cor": resultado.cor,
                    "ano": resultado.ano,
                    "provedor": resultado.provedor,
                },
            )

            # Verifica divergência com dados manuais existentes se houver (Decisão 4)
            if viatura_existente:
                marca_viatura = viatura_existente.marca.strip().lower()
                marca_api = resultado.marca.strip().lower()
                if marca_viatura and marca_api and marca_viatura not in marca_api and marca_api not in marca_viatura:
                    resultado.divergente = True
                    resultado.detalhes_divergencia = (
                        f"Divergência detectada: Base local possui '{viatura_existente.marca} {viatura_existente.modelo}', "
                        f"mas a consulta externa retornou '{resultado.marca} {resultado.modelo}'."
                    )
        else:
            config.falhas_consecutivas += 1
            config.ultima_falha = agora
            config.ultimo_erro = resultado.mensagem[:300]

            # Se atingir 3 falhas seguidas, abre o circuito por 5 minutos
            if config.falhas_consecutivas >= 3:
                config.circuito_aberto_ate = agora + timedelta(minutes=5)

            config.save(update_fields=["falhas_consecutivas", "ultima_falha", "ultimo_erro", "circuito_aberto_ate", "atualizado_em"])

        return resultado


_instancia_orquestrador = OrquestradorConsultaPlaca()


def consultar_placa(placa: str, forcar_api: bool = False) -> ResultadoConsulta:
    """Função pública de alto nível para consulta de veículo por placa."""
    return _instancia_orquestrador.consultar(placa, forcar_api=forcar_api)
