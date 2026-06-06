from django.contrib import admin

from .models import DisponibilidadeProfessor, Professor, Turma


def marcar_como_ativo(modeladmin, request, queryset):
    queryset.update(ativo=True)

marcar_como_ativo.short_description = "marcar como ativo"


def marcar_como_inativo(modeladmin, request, queryset):
    queryset.update(ativo=False)

marcar_como_inativo.short_description = "marcar como inativo"


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ("nome", "email", "especialidade", "carga_horaria_maxima", "ativo")
    list_filter = ("ativo", "especialidade")
    search_fields = ("nome", "email", "especialidade")
    readonly_fields = ("criado_em", "atualizado_em")
    actions = (marcar_como_ativo, marcar_como_inativo)


@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ("nome", "curso", "periodo_letivo", "turno", "numero_alunos", "ativo")
    list_filter = ("ativo", "curso", "periodo_letivo", "turno")
    search_fields = ("nome", "curso__nome", "curso__codigo")
    autocomplete_fields = ("curso", "periodo_letivo")
    readonly_fields = ("criado_em", "atualizado_em")
    list_select_related = ("curso", "periodo_letivo")
    actions = (marcar_como_ativo, marcar_como_inativo)


@admin.register(DisponibilidadeProfessor)
class DisponibilidadeProfessorAdmin(admin.ModelAdmin):
    list_display = ("professor", "horario", "disponivel", "observacao")
    list_filter = ("disponivel", "horario__dia_semana")
    search_fields = ("professor__nome", "professor__email")
    autocomplete_fields = ("professor", "horario")
    readonly_fields = ("criado_em", "atualizado_em")
    list_select_related = ("professor", "horario")