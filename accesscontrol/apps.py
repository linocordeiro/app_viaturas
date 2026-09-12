from django.apps import AppConfig


class AccessControlConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accesscontrol"
    verbose_name = "Controle de Acesso"

    def ready(self):
        import accesscontrol.signals  # noqa: F401

        # O signal m2m_changed precisa da classe real do model,
        # por isso é conectado aqui, após todos os apps estarem carregados
        from accesscontrol.signals import conectar_signal_m2m
        conectar_signal_m2m()
