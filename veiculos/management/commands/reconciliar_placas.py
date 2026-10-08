from django.core.management.base import BaseCommand
from django.utils import timezone

from services.consulta_placa import consultar_placa
from veiculos.models import Viatura


class Command(BaseCommand):
    help = "Reconcilia placas registradas em contingência manual contra a API externa e sinaliza divergências."

    def add_arguments(self, parser):
        parser.add_argument(
            "--placa",
            type=str,
            help="Reconcilia uma placa específica (ex: BRA2E19)",
        )
        parser.add_argument(
            "--todas",
            action="store_true",
            help="Força reconsulta de todos os veículos cadastrados",
        )

    def handle(self, *args, **options):
        placa_arg = options.get("placa")
        todas = options.get("todas")

        qs = Viatura.objects.all()
        if placa_arg:
            qs = qs.filter(placa=placa_arg.upper().strip())
        elif not todas:
            # Por padrão, apenas veículos manuais ou pendentes de classificação
            qs = qs.filter(origem_dados=Viatura.ORIGEM_MANUAL) | qs.filter(classificacao=Viatura.CLASSIFICACAO_PENDENTE)

        total = qs.count()
        self.stdout.write(f"Iniciando reconciliação de {total} veículo(s)...")

        divergencias_encontradas = 0
        sucessos = 0
        falhas = 0

        for v in qs:
            self.stdout.write(f"Consultando {v.placa} ({v.marca} {v.modelo})... ", ending="")
            res = consultar_placa(v.placa, forcar_api=True)

            if res.sucesso:
                sucessos += 1
                marca_atual = (v.marca or "").strip().lower()
                marca_api = (res.marca or "").strip().lower()

                # Verifica se há divergência semântica relevante
                if marca_atual and marca_api and marca_atual not in marca_api and marca_api not in marca_atual:
                    divergencias_encontradas += 1
                    msg_div = (
                        f"Divergência detectada: Registrado: '{v.marca} {v.modelo}' | "
                        f"Retornado pela API ({res.provedor}): '{res.marca} {res.modelo}'"
                    )
                    v.divergencia_dados = msg_div
                    v.save(update_fields=["divergencia_dados"])
                    self.stdout.write(self.style.WARNING(f"[DIVERGÊNCIA SINALIZADA] {msg_div}"))
                else:
                    if not v.cor and res.cor:
                        v.cor = res.cor
                        v.save(update_fields=["cor"])
                    self.stdout.write(self.style.SUCCESS("[OK - DADOS CONVERGENTES]"))
            else:
                falhas += 1
                self.stdout.write(self.style.NOTICE(f"[INDISPONÍVEL] {res.mensagem}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"\nReconciliação finalizada! Sucessos: {sucessos} | Divergências: {divergencias_encontradas} | Falhas: {falhas}"
            )
        )
