import contextvars

_current_db = contextvars.ContextVar("current_db", default="desenvolvimento")


def set_current_db(db_name: str):
    """Define o alias de banco de dados ativo no contexto atual."""
    _current_db.set(db_name)


def get_current_db() -> str:
    """Retorna o alias do banco de dados ativo no contexto atual."""
    return _current_db.get()


class DynamicDatabaseRouter:
    """
    Roteador de banco de dados para garantir compatibilidade e isolamento.
    Retorna None para permitir que o Django utilize a conexão 'default'
    dinamicamente configurada pelo DynamicDatabaseMiddleware.
    """

    def db_for_read(self, model, **hints):
        return None

    def db_for_write(self, model, **hints):
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db in ("default", "desenvolvimento", "producao")
