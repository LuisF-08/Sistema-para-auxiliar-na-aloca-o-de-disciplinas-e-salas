from .models import PeriodoLetivo


def periodo_atual(request):
    """injeta o periodo letivo corrente em todos os templates.
    """
    return {
        'periodo_atual_global': PeriodoLetivo.atual(),
    }