from pessoas.models import DisponibilidadeProfessor, Professor
from alocacao.repositories.alocacoes import alocacoes_ativas


def professores_disponiveis(periodo_letivo, horario):
    """lista professores ativos sem aula e sem bloqueio no horario."""

    professores_ocupados = alocacoes_ativas(periodo_letivo).filter(horario=horario)
    professores_indisponiveis = DisponibilidadeProfessor.objects.filter(
        horario=horario,
        disponivel=False,
    )

    return (
        Professor.objects.filter(ativo=True)
        .exclude(id__in=professores_ocupados.values("professor_id"))
        .exclude(id__in=professores_indisponiveis.values("professor_id"))
        .order_by("nome")
    )
