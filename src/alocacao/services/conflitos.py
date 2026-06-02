from django.core.exceptions import ValidationError


def mapear_conflitos(alocacao):
    """retorna conflitos da alocacao sem salvar nada no banco."""

    try:
        alocacao.full_clean()
    except ValidationError as erro:
        if hasattr(erro, "message_dict"):
            return erro.message_dict
        return {"__all__": erro.messages}

    return {}


def possui_conflito(alocacao):
    """retorna s quando a alocacao candidata possui algum conflito."""

    return bool(mapear_conflitos(alocacao))


def validar_sem_conflito(alocacao):
    """valida uma alocacao candidata e levanta erro se houver conflito."""

    conflitos = mapear_conflitos(alocacao)
    if conflitos:
        raise ValidationError(conflitos)
    return alocacao
