from django.contrib import admin
from django.contrib import messages
from django.core.exceptions import ValidationError

from .models import Alocacao, Horario


def confirmar_alocacoes(modeladmin, request, queryset):
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
    total = 0
    for alocacao in queryset:
        alocacao.status = Alocacao.Status.CANCELADA
        alocacao.save()
        total += 1
    modeladmin.message_user(request, f"{total} alocação(ões) cancelada(s).")

cancelar_alocacoes.short_description = "cancelar alocações"


@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ("dia_semana", "horario_inicio", "horario_fim", "ativo")
    list_filter = ("ativo", "dia_semana")
    search_fields = ("=dia_semana",)
    readonly_fields = ("criado_em", "atualizado_em")


@admin.register(Alocacao)
class AlocacaoAdmin(admin.ModelAdmin):
    list_display = (
        "periodo_letivo", "disciplina", "professor",
        "turma", "sala", "horario", "status",
    )
    list_filter = (
        "periodo_letivo", "status", "horario__dia_semana",
        "disciplina__curso", "sala__tipo_sala",
    )
    search_fields = (
        "disciplina__nome", "disciplina__codigo", "professor__nome",
        "turma__nome", "sala__nome",
    )
    autocomplete_fields = (
        "periodo_letivo", "professor", "disciplina",
        "turma", "sala", "horario",
    )
    readonly_fields = ("criado_em", "atualizado_em")
    list_select_related = (
        "periodo_letivo", "professor", "disciplina",
        "turma", "sala", "horario",
    )
    actions = (confirmar_alocacoes, cancelar_alocacoes)