from django.contrib import admin
from django.contrib import messages
from django.core.exceptions import ValidationError

from .models import (
    Alocacao,
    Curso,
    Disciplina,
    DisponibilidadeProfessor,
    Horario,
    PeriodoLetivo,
    Professor,
    RecursoSala,
    Sala,
    Turma,
)


def marcar_como_ativo(modeladmin, request, queryset):
    """marca os registros selecionados como ativos."""

    queryset.update(ativo=True)


marcar_como_ativo.short_description = "marcar como ativo"


def marcar_como_inativo(modeladmin, request, queryset):
    """marca os registros selecionados como inativos."""

    queryset.update(ativo=False)


marcar_como_inativo.short_description = "marcar como inativo"


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nome", "ativo", "criado_em", "atualizado_em")
    list_filter = ("ativo",)
    search_fields = ("codigo", "nome")
    readonly_fields = ("criado_em", "atualizado_em")
    actions = (marcar_como_ativo, marcar_como_inativo)


@admin.register(PeriodoLetivo)
class PeriodoLetivoAdmin(admin.ModelAdmin):
    list_display = (
        "ano",
        "semestre",
        "data_inicio",
        "data_fim",
        "ativo",
        "criado_em",
        "atualizado_em",
    )
    list_filter = ("ativo", "ano", "semestre")
    search_fields = ("=ano", "=semestre")
    readonly_fields = ("criado_em", "atualizado_em")
    actions = (marcar_como_ativo, marcar_como_inativo)


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "email",
        "especialidade",
        "carga_horaria_maxima",
        "ativo",
    )
    list_filter = ("ativo", "especialidade")
    search_fields = ("nome", "email", "especialidade")
    readonly_fields = ("criado_em", "atualizado_em")
    actions = (marcar_como_ativo, marcar_como_inativo)


@admin.register(RecursoSala)
class RecursoSalaAdmin(admin.ModelAdmin):
    list_display = ("nome", "descricao", "criado_em", "atualizado_em")
    search_fields = ("nome", "descricao")
    readonly_fields = ("criado_em", "atualizado_em")


@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "nome",
        "curso",
        "carga_horaria_semanal",
        "periodo_recomendado",
        "ativo",
    )
    list_filter = ("ativo", "curso", "periodo_recomendado")
    search_fields = ("codigo", "nome", "curso__nome", "curso__codigo")
    autocomplete_fields = ("curso",)
    filter_horizontal = ("recursos_necessarios",)
    readonly_fields = ("criado_em", "atualizado_em")
    actions = (marcar_como_ativo, marcar_como_inativo)


@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "curso",
        "periodo_letivo",
        "turno",
        "numero_alunos",
        "ativo",
    )
    list_filter = ("ativo", "curso", "periodo_letivo", "turno")
    search_fields = (
        "nome",
        "curso__nome",
        "curso__codigo",
        "periodo_letivo__ano",
        "periodo_letivo__semestre",
    )
    autocomplete_fields = ("curso", "periodo_letivo")
    readonly_fields = ("criado_em", "atualizado_em")
    list_select_related = ("curso", "periodo_letivo")
    actions = (marcar_como_ativo, marcar_como_inativo)


@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "tipo_sala",
        "capacidade_alunos",
        "localizacao",
        "ativo",
    )
    list_filter = ("ativo", "tipo_sala", "recursos")
    search_fields = ("nome", "localizacao")
    filter_horizontal = ("recursos",)
    readonly_fields = ("criado_em", "atualizado_em")
    actions = (marcar_como_ativo, marcar_como_inativo)


@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ("dia_semana", "horario_inicio", "horario_fim", "ativo")
    list_filter = ("ativo", "dia_semana")
    search_fields = ("=dia_semana",)
    readonly_fields = ("criado_em", "atualizado_em")
    actions = (marcar_como_ativo, marcar_como_inativo)


@admin.register(DisponibilidadeProfessor)
class DisponibilidadeProfessorAdmin(admin.ModelAdmin):
    list_display = ("professor", "horario", "disponivel", "observacao")
    list_filter = ("disponivel", "horario__dia_semana")
    search_fields = ("professor__nome", "professor__email", "observacao")
    autocomplete_fields = ("professor", "horario")
    readonly_fields = ("criado_em", "atualizado_em")
    list_select_related = ("professor", "horario")


def confirmar_alocacoes(modeladmin, request, queryset):
    """confirma alocações planejadas selecionadas."""

    total = 0
    for alocacao in queryset:
        alocacao.status = Alocacao.Status.CONFIRMADA
        try:
            alocacao.save()
            total += 1
        except ValidationError as erro:
            modeladmin.message_user(request, erro, level=messages.ERROR)

    modeladmin.message_user(request, f"{total} alocação(ões) confirmada(s).")


confirmar_alocacoes.short_description = "confirmar alocações"


def cancelar_alocacoes(modeladmin, request, queryset):
    """cancela alocações selecionadas."""

    total = 0
    for alocacao in queryset:
        alocacao.status = Alocacao.Status.CANCELADA
        alocacao.save()
        total += 1

    modeladmin.message_user(request, f"{total} alocação(ões) cancelada(s).")


cancelar_alocacoes.short_description = "cancelar alocações"


@admin.register(Alocacao)
class AlocacaoAdmin(admin.ModelAdmin):
    list_display = (
        "periodo_letivo",
        "disciplina",
        "professor",
        "turma",
        "sala",
        "horario",
        "status",
    )
    list_filter = (
        "periodo_letivo",
        "status",
        "horario__dia_semana",
        "disciplina__curso",
        "sala__tipo_sala",
    )
    search_fields = (
        "disciplina__nome",
        "disciplina__codigo",
        "professor__nome",
        "turma__nome",
        "sala__nome",
        "periodo_letivo__ano",
        "periodo_letivo__semestre",
    )
    autocomplete_fields = (
        "periodo_letivo",
        "professor",
        "disciplina",
        "turma",
        "sala",
        "horario",
    )
    readonly_fields = ("criado_em", "atualizado_em")
    list_select_related = (
        "periodo_letivo",
        "professor",
        "disciplina",
        "turma",
        "sala",
        "horario",
    )
    actions = (confirmar_alocacoes, cancelar_alocacoes)
