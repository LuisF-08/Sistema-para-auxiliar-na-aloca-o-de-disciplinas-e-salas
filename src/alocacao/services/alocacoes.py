from alocacao.models import Alocacao


def criar_alocacao(
    *,
    periodo_letivo,
    professor,
    disciplina,
    turma,
    sala,
    horario,
    status=Alocacao.Status.PLANEJADA,
    observacao="",
):
    """cria uma alocacao validando todas as regras antes de salvar."""

    alocacao = Alocacao(
        periodo_letivo=periodo_letivo,
        professor=professor,
        disciplina=disciplina,
        turma=turma,
        sala=sala,
        horario=horario,
        status=status,
        observacao=observacao,
    )
    alocacao.full_clean()
    alocacao.save()
    return alocacao


def confirmar_alocacao(alocacao):
    """confirma uma alocacao planejada."""

    alocacao.status = Alocacao.Status.CONFIRMADA
    alocacao.save()
    return alocacao


def cancelar_alocacao(alocacao):
    """cancela uma alocacao e libera seu horario para novas alocacoes."""

    alocacao.status = Alocacao.Status.CANCELADA
    alocacao.save()
    return alocacao
