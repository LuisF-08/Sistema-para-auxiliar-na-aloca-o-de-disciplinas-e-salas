from django.contrib import admin

from .models import RecursoSala, Sala


def marcar_como_ativo(modeladmin, request, queryset):
    queryset.update(ativo=True)

marcar_como_ativo.short_description = "marcar como ativo"


def marcar_como_inativo(modeladmin, request, queryset):
    queryset.update(ativo=False)

marcar_como_inativo.short_description = "marcar como inativo"


@admin.register(RecursoSala)
class RecursoSalaAdmin(admin.ModelAdmin):
    list_display = ("nome", "descricao", "criado_em", "atualizado_em")
    search_fields = ("nome", "descricao")
    readonly_fields = ("criado_em", "atualizado_em")


@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ("nome", "tipo_sala", "capacidade_alunos", "localizacao", "ativo")
    list_filter = ("ativo", "tipo_sala", "recursos")
    search_fields = ("nome", "localizacao")
    filter_horizontal = ("recursos",)
    readonly_fields = ("criado_em", "atualizado_em")
    actions = (marcar_como_ativo, marcar_como_inativo)