from django.contrib import admin

from .models import Curso, Disciplina, PeriodoLetivo


def marcar_como_ativo(modeladmin, request, queryset):
    queryset.update(ativo=True)

marcar_como_ativo.short_description = "marcar como ativo"


def marcar_como_inativo(modeladmin, request, queryset):
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
    list_display = ("ano", "semestre", "data_inicio", "data_fim", "ativo")
    list_filter = ("ativo", "ano", "semestre")
    search_fields = ("=ano", "=semestre")
    readonly_fields = ("criado_em", "atualizado_em")
    actions = (marcar_como_ativo, marcar_como_inativo)


@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = (
        "codigo", "nome", "curso",
        "carga_horaria_semanal", "periodo_recomendado", "ativo",
    )
    list_filter = ("ativo", "curso", "periodo_recomendado")
    search_fields = ("codigo", "nome", "curso__nome", "curso__codigo")
    autocomplete_fields = ("curso",)
    filter_horizontal = ("recursos_necessarios",)
    readonly_fields = ("criado_em", "atualizado_em")
    actions = (marcar_como_ativo, marcar_como_inativo)