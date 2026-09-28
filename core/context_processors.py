def ambiente_context(request):
    """
    Disponibiliza flags de ambiente, banco de dados ativo e indicador
    para todos os templates do sistema.
    """
    return {
        "is_db_desenvolvimento": getattr(request, "is_db_desenvolvimento", True),
        "db_env": getattr(request, "db_env", "desenvolvimento"),
    }
