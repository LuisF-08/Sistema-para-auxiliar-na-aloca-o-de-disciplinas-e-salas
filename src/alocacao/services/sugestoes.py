"""
Serviço de auto-sugestão de alocação.

Quando uma alocação candidata possui conflitos, este módulo gera
alternativas viáveis (salas livres, horários livres) para que o
coordenador possa resolver o conflito com um clique.
"""

from alocacao.models import Alocacao, Horario, STATUS_ATIVOS_ALOCACAO
from infraestrutura.models import Sala
from pessoas.models import DisponibilidadeProfessor


def _salas_ocupadas_no_horario(periodo_letivo_id, horario_id, excluir_alocacao_id=None):
    """Retorna IDs de salas que já possuem alocação ativa neste horário/período."""
    qs = Alocacao.objects.filter(
        periodo_letivo_id=periodo_letivo_id,
        horario_id=horario_id,
        status__in=STATUS_ATIVOS_ALOCACAO,
    )
    if excluir_alocacao_id:
        qs = qs.exclude(pk=excluir_alocacao_id)
    return set(qs.values_list("sala_id", flat=True))


def _professores_ocupados_no_horario(periodo_letivo_id, horario_id, excluir_alocacao_id=None):
    """Retorna IDs de professores que já possuem alocação ativa neste horário/período."""
    qs = Alocacao.objects.filter(
        periodo_letivo_id=periodo_letivo_id,
        horario_id=horario_id,
        status__in=STATUS_ATIVOS_ALOCACAO,
    )
    if excluir_alocacao_id:
        qs = qs.exclude(pk=excluir_alocacao_id)
    return set(qs.values_list("professor_id", flat=True))


def _turmas_ocupadas_no_horario(periodo_letivo_id, horario_id, excluir_alocacao_id=None):
    """Retorna IDs de turmas que já possuem alocação ativa neste horário/período."""
    qs = Alocacao.objects.filter(
        periodo_letivo_id=periodo_letivo_id,
        horario_id=horario_id,
        status__in=STATUS_ATIVOS_ALOCACAO,
    )
    if excluir_alocacao_id:
        qs = qs.exclude(pk=excluir_alocacao_id)
    return set(qs.values_list("turma_id", flat=True))


def sugerir_salas_alternativas(periodo_letivo_id, horario_id, capacidade_minima=0):
    """
    Retorna salas ativas que estão LIVRES no horário/período informado
    e possuem capacidade >= capacidade_minima.
    """
    salas_ocupadas = _salas_ocupadas_no_horario(periodo_letivo_id, horario_id)

    qs = Sala.objects.filter(ativo=True).exclude(id__in=salas_ocupadas)
    if capacidade_minima and capacidade_minima > 0:
        qs = qs.filter(capacidade_alunos__gte=capacidade_minima)

    return qs.order_by("nome")[:10]


def sugerir_horarios_alternativos(periodo_letivo_id, professor_id=None, turma_id=None, sala_id=None):
    """
    Retorna horários ativos onde TODOS os recursos informados estão livres.
    """
    horarios_ativos = Horario.objects.filter(ativo=True)
    horarios_bloqueados = set()

    for horario in horarios_ativos:
        # Verifica conflito de professor
        if professor_id:
            profs_ocupados = _professores_ocupados_no_horario(periodo_letivo_id, horario.id)
            if professor_id in profs_ocupados:
                horarios_bloqueados.add(horario.id)
                continue

            # Verifica disponibilidade do professor
            if DisponibilidadeProfessor.objects.filter(
                professor_id=professor_id,
                horario_id=horario.id,
                disponivel=False,
            ).exists():
                horarios_bloqueados.add(horario.id)
                continue

        # Verifica conflito de turma
        if turma_id:
            turmas_ocupadas = _turmas_ocupadas_no_horario(periodo_letivo_id, horario.id)
            if turma_id in turmas_ocupadas:
                horarios_bloqueados.add(horario.id)
                continue

        # Verifica conflito de sala
        if sala_id:
            salas_ocupadas = _salas_ocupadas_no_horario(periodo_letivo_id, horario.id)
            if sala_id in salas_ocupadas:
                horarios_bloqueados.add(horario.id)
                continue

    return (
        horarios_ativos
        .exclude(id__in=horarios_bloqueados)
        .order_by("dia_semana", "horario_inicio")[:10]
    )


def detectar_conflitos(periodo_letivo_id, professor_id, sala_id, horario_id, turma_id):
    """
    Analisa uma alocação candidata e retorna um dict com os conflitos encontrados.
    """
    conflitos = []

    if not all([periodo_letivo_id, horario_id]):
        return conflitos

    # Conflito de sala
    if sala_id:
        salas_ocupadas = _salas_ocupadas_no_horario(periodo_letivo_id, horario_id)
        if int(sala_id) in salas_ocupadas:
            # Descobre qual alocação ocupa a sala
            alocacao_conflito = Alocacao.objects.filter(
                periodo_letivo_id=periodo_letivo_id,
                horario_id=horario_id,
                sala_id=sala_id,
                status__in=STATUS_ATIVOS_ALOCACAO,
            ).select_related("disciplina", "professor").first()

            desc = "A sala já possui uma aula alocada neste horário."
            if alocacao_conflito:
                desc = (
                    f"Sala ocupada por: {alocacao_conflito.disciplina.nome} "
                    f"(Prof. {alocacao_conflito.professor.nome})"
                )
            conflitos.append({"tipo": "sala", "mensagem": desc})

    # Conflito de professor
    if professor_id:
        profs_ocupados = _professores_ocupados_no_horario(periodo_letivo_id, horario_id)
        if int(professor_id) in profs_ocupados:
            alocacao_conflito = Alocacao.objects.filter(
                periodo_letivo_id=periodo_letivo_id,
                horario_id=horario_id,
                professor_id=professor_id,
                status__in=STATUS_ATIVOS_ALOCACAO,
            ).select_related("disciplina", "sala").first()

            desc = "O professor já possui uma aula neste horário."
            if alocacao_conflito:
                desc = (
                    f"Professor já alocado em: {alocacao_conflito.disciplina.nome} "
                    f"(Sala {alocacao_conflito.sala.nome})"
                )
            conflitos.append({"tipo": "professor", "mensagem": desc})

        # Indisponibilidade do professor
        if DisponibilidadeProfessor.objects.filter(
            professor_id=professor_id,
            horario_id=horario_id,
            disponivel=False,
        ).exists():
            conflitos.append({
                "tipo": "professor",
                "mensagem": "O professor está marcado como indisponível neste horário."
            })

    # Conflito de turma
    if turma_id:
        turmas_ocupadas = _turmas_ocupadas_no_horario(periodo_letivo_id, horario_id)
        if int(turma_id) in turmas_ocupadas:
            alocacao_conflito = Alocacao.objects.filter(
                periodo_letivo_id=periodo_letivo_id,
                horario_id=horario_id,
                turma_id=turma_id,
                status__in=STATUS_ATIVOS_ALOCACAO,
            ).select_related("disciplina", "sala").first()

            desc = "A turma já possui uma aula neste horário."
            if alocacao_conflito:
                desc = (
                    f"Turma já alocada em: {alocacao_conflito.disciplina.nome} "
                    f"(Sala {alocacao_conflito.sala.nome})"
                )
            conflitos.append({"tipo": "turma", "mensagem": desc})

    return conflitos


def gerar_sugestoes(periodo_letivo_id, professor_id, sala_id, horario_id, turma_id, num_alunos=0):
    """
    Função principal: detecta conflitos e retorna sugestões alternativas.

    Retorna:
        {
            "conflitos": [...],
            "sugestoes_salas": [...],
            "sugestoes_horarios": [...],
        }
    """
    conflitos = detectar_conflitos(
        periodo_letivo_id, professor_id, sala_id, horario_id, turma_id
    )

    sugestoes_salas = []
    sugestoes_horarios = []

    if conflitos:
        tipos_conflito = {c["tipo"] for c in conflitos}

        # Se há conflito de sala, sugere salas alternativas
        if "sala" in tipos_conflito and horario_id and periodo_letivo_id:
            salas = sugerir_salas_alternativas(
                periodo_letivo_id, horario_id, capacidade_minima=num_alunos
            )
            sugestoes_salas = [
                {
                    "id": s.id,
                    "nome": s.nome,
                    "tipo": s.tipo_sala,
                    "capacidade": s.capacidade_alunos,
                    "localizacao": s.localizacao or "",
                }
                for s in salas
            ]

        # Se há conflito de professor, turma ou sala, sugere horários alternativos
        if tipos_conflito & {"professor", "turma", "sala"}:
            horarios = sugerir_horarios_alternativos(
                periodo_letivo_id,
                professor_id=int(professor_id) if professor_id else None,
                turma_id=int(turma_id) if turma_id else None,
                sala_id=int(sala_id) if sala_id else None,
            )
            DIA_NOMES = {
                "1": "Segunda-feira",
                "2": "Terça-feira",
                "3": "Quarta-feira",
                "4": "Quinta-feira",
                "5": "Sexta-feira",
                "6": "Sábado",
            }
            sugestoes_horarios = [
                {
                    "id": h.id,
                    "dia_semana": h.dia_semana,
                    "dia_nome": DIA_NOMES.get(str(h.dia_semana), str(h.dia_semana)),
                    "horario_inicio": h.horario_inicio.strftime("%H:%M"),
                    "horario_fim": h.horario_fim.strftime("%H:%M"),
                }
                for h in horarios
            ]

    return {
        "conflitos": conflitos,
        "sugestoes_salas": sugestoes_salas,
        "sugestoes_horarios": sugestoes_horarios,
    }
