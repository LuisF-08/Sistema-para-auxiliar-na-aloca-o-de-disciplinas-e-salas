from infraestrutura.models import Sala
from alocacao.repositories.alocacoes import alocacoes_ativas


def salas_livres(periodo_letivo, horario, capacidade_minima=None, recursos=None):
    """lista salas ativas livres no periodo/horario informado."""

    salas_ocupadas = alocacoes_ativas(periodo_letivo).filter(horario=horario)
    queryset = Sala.objects.filter(ativo=True).exclude(
        id__in=salas_ocupadas.values("sala_id")
    )

    if capacidade_minima:
        queryset = queryset.filter(capacidade_alunos__gte=capacidade_minima)

    if recursos:
        for recurso in recursos:
            queryset = queryset.filter(recursos=recurso)

    return queryset.distinct().order_by("nome")
