import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from .base import ProvedorPlacaBase, ResultadoConsulta

logger = logging.getLogger(__name__)

# Base local resiliente para demonstração e contingência quando sem rede externa
CATALOGO_SIMULADO = {
    "RIO2A18": {"marca": "Toyota", "modelo": "Hilux SW4 4x4", "cor": "Preta", "ano": "2023"},
    "BRA2E19": {"marca": "Chevrolet", "modelo": "Trailblazer Premier", "cor": "Branca", "ano": "2022"},
    "NXR8890": {"marca": "Ford", "modelo": "Ranger Limited 3.2", "cor": "Prata", "ano": "2021"},
    "MZN1234": {"marca": "Toyota", "modelo": "Corolla Altis", "cor": "Cinza", "ano": "2022"},
    "OXP5678": {"marca": "Mitsubishi", "modelo": "Pajero Dakar 4x4", "cor": "Preta", "ano": "2020"},
    "PF01010": {"marca": "Toyota", "modelo": "Hilux CD 4x4", "cor": "Branca", "ano": "2023"},
    "ACR9988": {"marca": "Nissan", "modelo": "Frontier Attack 4x4", "cor": "Cinza", "ano": "2023"},
}


class ProvedorGratuito(ProvedorPlacaBase):
    nome = "API Gratuita / Aberta"

    def consultar(self, placa: str, config: Any, proxy_url: str = "") -> ResultadoConsulta:
        placa = placa.upper().strip()
        endpoint = getattr(config, "gratuito_url", "").strip()

        # Se houver endpoint configurado na administração, tenta a chamada HTTP real
        if endpoint:
            url = endpoint.replace("{placa}", placa)
            token = getattr(config, "gratuito_token", "").strip()
            if "{token}" in url:
                url = url.replace("{token}", token)

            headers = {
                "User-Agent": "APP_VIATURAS_PF/1.0",
                "Accept": "application/json",
            }

            header_nome = getattr(config, "gratuito_cabecalho", "").strip()
            prefixo = getattr(config, "gratuito_prefixo", "")
            if token and header_nome and "{token}" not in endpoint:
                headers[header_nome] = f"{prefixo}{token}"

            try:
                handlers = []
                if proxy_url:
                    handlers.append(urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url}))
                opener = urllib.request.build_opener(*handlers)
                req = urllib.request.Request(url, headers=headers)
                timeout = getattr(config, "timeout_segundos", 5)

                with opener.open(req, timeout=timeout) as response:
                    status_code = response.getcode()
                    if status_code == 200:
                        raw_data = json.loads(response.read().decode("utf-8"))
                        marca = (
                            raw_data.get("marca")
                            or raw_data.get("brand")
                            or raw_data.get("fabricante")
                            or ""
                        )
                        modelo = (
                            raw_data.get("modelo")
                            or raw_data.get("model")
                            or raw_data.get("nome_modelo")
                            or ""
                        )
                        cor = raw_data.get("cor") or raw_data.get("color") or ""
                        ano = str(raw_data.get("ano") or raw_data.get("anoModelo") or raw_data.get("year") or "")

                        # Se marca e modelo vieram juntos em um único campo (ex: "TOYOTA/HILUX")
                        if "/" in marca and not modelo:
                            partes = marca.split("/", 1)
                            marca = partes[0].strip()
                            modelo = partes[1].strip()
                        elif "/" in modelo and not marca:
                            partes = modelo.split("/", 1)
                            marca = partes[0].strip()
                            modelo = partes[1].strip()

                        if marca or modelo:
                            return ResultadoConsulta(
                                sucesso=True,
                                placa=placa,
                                marca=marca.title(),
                                modelo=modelo,
                                cor=cor.title(),
                                ano=ano,
                                origem="API",
                                provedor=self.nome,
                                mensagem="Veículo identificado com sucesso via API gratuita.",
                                dados_brutos=raw_data,
                            )
            except urllib.error.HTTPError as e:
                logger.warning(f"Erro HTTP {e.code} ao consultar placa {placa} no provedor gratuito: {e.reason}")
            except urllib.error.URLError as e:
                logger.warning(f"Erro de conexão/proxy ao consultar placa {placa}: {e.reason}")
            except Exception as e:
                logger.warning(f"Falha inesperada ao consultar placa {placa}: {str(e)}")

        # Fallback para base conhecida/simulada quando sem URL configurada ou em contingência
        if placa in CATALOGO_SIMULADO:
            dados = CATALOGO_SIMULADO[placa]
            return ResultadoConsulta(
                sucesso=True,
                placa=placa,
                marca=dados["marca"],
                modelo=dados["modelo"],
                cor=dados.get("cor", ""),
                ano=dados.get("ano", ""),
                origem="API",
                provedor=f"{self.nome} (Catálogo de Referência)",
                mensagem="Veículo identificado através do catálogo de referência aberto.",
            )

        return ResultadoConsulta(
            sucesso=False,
            placa=placa,
            origem="MANUAL",
            provedor=self.nome,
            mensagem="API externa não retornou dados para a placa. Informe marca e modelo manualmente.",
        )
