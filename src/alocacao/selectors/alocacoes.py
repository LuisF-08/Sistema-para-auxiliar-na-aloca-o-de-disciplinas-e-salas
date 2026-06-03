from django.db.models import Count, Sum

from alocacao.models import Alocacao, STATUS_ATIVOS_ALOCACAO


def alocacoes_ativas(periodo_letivo=None):
    """retorna alocacoes que ainda contam para grade e conflitos."""

    queryset = Alocacao.objects.filter(status__in=STATUS_ATIVOS_ALOCACAO)
    if periodo_letivo:
        queryset = queryset.filter(periodo_letivo=periodo_letivo)
    return queryset.select_related(
        "periodo_letivo",
        "professor",
        "disciplina",
        "turma",
        "sala",
        "horario",
    )


def carga_horaria_professor(professor, periodo_letivo):
    """soma a carga semanal do professor em um periodo letivo."""

    return (
        alocacoes_ativas(periodo_letivo)
        .filter(professor=professor)
        .aggregate(total=Sum("disciplina__carga_horaria_semanal"))
        .get("total")
        or 0
    )


def ocupacao_por_sala(periodo_letivo):
    """retorna qtd de alocacoes ativas por sala no periodo."""

    return (
        alocacoes_ativas(periodo_letivo)
        .values("sala_id", "sala__nome", "sala__capacidade_alunos")
        .annotate(total_alocacoes=Count("id"))
        .order_by("sala__nome")
    )
