import base64
import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from .base import ProvedorPlacaBase, ResultadoConsulta

logger = logging.getLogger(__name__)


class ProvedorSerpro(ProvedorPlacaBase):
    nome = "SERPRO / SENATRAN (Oficial)"

    def _obter_token(self, config: Any, proxy_url: str = "") -> str:
        url_token = getattr(config, "serpro_url_token", "").strip()
        consumer_key = getattr(config, "serpro_consumer_key", "").strip()
        consumer_secret = getattr(config, "serpro_consumer_secret", "").strip()

        if not (url_token and consumer_key and consumer_secret):
            return ""

        auth_str = f"{consumer_key}:{consumer_secret}"
        auth_b64 = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")

        headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "APP_VIATURAS_PF/1.0",
        }
        data = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode("utf-8")

        handlers = []
        if proxy_url:
            handlers.append(urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url}))
        opener = urllib.request.build_opener(*handlers)
        req = urllib.request.Request(url_token, data=data, headers=headers)

        with opener.open(req, timeout=getattr(config, "timeout_segundos", 5)) as resp:
            if resp.getcode() == 200:
                res = json.loads(resp.read().decode("utf-8"))
                return res.get("access_token", "")
        return ""

    def consultar(self, placa: str, config: Any, proxy_url: str = "") -> ResultadoConsulta:
        placa = placa.upper().strip()
        url_consulta = getattr(config, "serpro_url_consulta", "").strip()

        if not url_consulta:
            return ResultadoConsulta(
                sucesso=False,
                placa=placa,
                origem="MANUAL",
                provedor=self.nome,
                mensagem="URL de consulta SERPRO não configurada no painel administrativo.",
            )

        try:
            token = self._obter_token(config, proxy_url)
            headers = {
                "User-Agent": "APP_VIATURAS_PF/1.0",
                "Accept": "application/json",
            }
            if token:
                headers["Authorization"] = f"Bearer {token}"

            url = url_consulta.replace("{placa}", placa)
            handlers = []
            if proxy_url:
                handlers.append(urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url}))
            opener = urllib.request.build_opener(*handlers)
            req = urllib.request.Request(url, headers=headers)
            timeout = getattr(config, "timeout_segundos", 5)

            with opener.open(req, timeout=timeout) as response:
                if response.getcode() == 200:
                    raw_data = json.loads(response.read().decode("utf-8"))
                    # Tratamento dos formatos usuais da API SENATRAN/SERPRO
                    marca_modelo = raw_data.get("marcaModelo") or raw_data.get("marca_modelo") or ""
                    cor = raw_data.get("cor") or raw_data.get("corVeiculo") or ""
                    ano = str(raw_data.get("anoModelo") or raw_data.get("anoFabricacao") or "")

                    marca = ""
                    modelo = ""
                    if "/" in marca_modelo:
                        partes = marca_modelo.split("/", 1)
                        marca = partes[0].strip()
                        modelo = partes[1].strip()
                    else:
                        marca = raw_data.get("marca") or marca_modelo
                        modelo = raw_data.get("modelo") or ""

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
                            mensagem="Veículo identificado com sucesso via API SERPRO / SENATRAN.",
                            dados_brutos=raw_data,
                        )
        except urllib.error.HTTPError as e:
            logger.warning(f"Erro HTTP {e.code} ao consultar SERPRO para placa {placa}: {e.reason}")
            return ResultadoConsulta(
                sucesso=False,
                placa=placa,
                origem="MANUAL",
                provedor=self.nome,
                mensagem=f"Erro {e.code} na API SERPRO. Modo contingência manual ativado.",
            )
        except urllib.error.URLError as e:
            logger.warning(f"Falha de conexão com SERPRO: {e.reason}")
            return ResultadoConsulta(
                sucesso=False,
                placa=placa,
                origem="MANUAL",
                provedor=self.nome,
                mensagem="Falha de conexão com a API SERPRO via proxy institucional. Modo contingência ativado.",
            )
        except Exception as e:
            logger.warning(f"Erro inesperado no provedor SERPRO: {str(e)}")

        return ResultadoConsulta(
            sucesso=False,
            placa=placa,
            origem="MANUAL",
            provedor=self.nome,
            mensagem="API SERPRO indisponível. Preencha marca e modelo manualmente.",
        )
