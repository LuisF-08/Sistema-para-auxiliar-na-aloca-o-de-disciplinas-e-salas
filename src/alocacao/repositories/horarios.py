from alocacao.models import Horario
from alocacao.repositories.alocacoes import alocacoes_ativas


def horarios_livres_para_turma(turma):
    """lista horarios ativos em que a turma ainda n possui aula."""

    horarios_ocupados = alocacoes_ativas(turma.periodo_letivo).filter(turma=turma)
    return (
        Horario.objects.filter(ativo=True)
        .exclude(id__in=horarios_ocupados.values("horario_id"))
        .order_by("dia_semana", "horario_inicio")
    )


def horarios_livres_para_professor(professor, periodo_letivo):
    """lista horarios ativos em que o professor ainda n possui aula."""

    horarios_ocupados = alocacoes_ativas(periodo_letivo).filter(professor=professor)
    return (
        Horario.objects.filter(ativo=True)
        .exclude(id__in=horarios_ocupados.values("horario_id"))
        .order_by("dia_semana", "horario_inicio")
    )
