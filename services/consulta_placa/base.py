from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class ResultadoConsulta:
    sucesso: bool
    placa: str
    marca: str = ""
    modelo: str = ""
    cor: str = ""
    ano: str = ""
    origem: str = "MANUAL"  # "API", "CACHE", "MANUAL", "FROTA"
    provedor: str = ""
    mensagem: str = ""
    divergente: bool = False
    detalhes_divergencia: str = ""
    dados_brutos: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sucesso": self.sucesso,
            "placa": self.placa,
            "marca": self.marca,
            "modelo": self.modelo,
            "cor": self.cor,
            "ano": self.ano,
            "origem": self.origem,
            "provedor": self.provedor,
            "mensagem": self.mensagem,
            "divergente": self.divergente,
            "detalhes_divergencia": self.detalhes_divergencia,
        }


class ProvedorPlacaBase:
    nome = "Base"

    def consultar(self, placa: str, config: Any, proxy_url: str = "") -> ResultadoConsulta:
        raise NotImplementedError
