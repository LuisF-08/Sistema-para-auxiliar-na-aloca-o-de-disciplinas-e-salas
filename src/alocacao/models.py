from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q, Sum


STATUS_ATIVOS_ALOCACAO = ["planejada", "confirmada"]


class Horario(models.Model):
    class DiaSemana(models.IntegerChoices):
        SEGUNDA = 1, "segunda-feira"
        TERCA = 2, "terca-feira"
        QUARTA = 3, "quarta-feira"
        QUINTA = 4, "quinta-feira"
        SEXTA = 5, "sexta-feira"
        SABADO = 6, "sabado"

    dia_semana = models.PositiveSmallIntegerField(choices=DiaSemana.choices)
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["dia_semana", "horario_inicio"]
        verbose_name = "horario"
        verbose_name_plural = "horarios"
        constraints = [
            models.UniqueConstraint(
                fields=["dia_semana", "horario_inicio", "horario_fim"],
                name="horario_faixa_unica",
            ),
            models.CheckConstraint(
                condition=Q(horario_fim__gt=models.F("horario_inicio")),
                name="horario_fim_maior_inicio",
            ),
        ]
        indexes = [
            models.Index(
                fields=["dia_semana", "horario_inicio"],
                name="horario_dia_inicio_idx",
            ),
        ]

    def __str__(self):
        dia = self.get_dia_semana_display()
        return f"{dia}, {self.horario_inicio:%H:%M} as {self.horario_fim:%H:%M}"


class Alocacao(models.Model):
    class Status(models.TextChoices):
        PLANEJADA = "planejada", "planejada"
        CONFIRMADA = "confirmada", "confirmada"
        CANCELADA = "cancelada", "cancelada"

    periodo_letivo = models.ForeignKey(
        "academico.PeriodoLetivo",
        on_delete=models.PROTECT,
        related_name="alocacoes",
    )
    professor = models.ForeignKey(
        "pessoas.Professor",
        on_delete=models.PROTECT,
        related_name="alocacoes",
    )
    disciplina = models.ForeignKey(
        "academico.Disciplina",
        on_delete=models.PROTECT,
        related_name="alocacoes",
    )
    turma = models.ForeignKey(
        "pessoas.Turma",
        on_delete=models.PROTECT,
        related_name="alocacoes",
    )
    sala = models.ForeignKey(
        "infraestrutura.Sala",
        on_delete=models.PROTECT,
        related_name="alocacoes",
    )
    horario = models.ForeignKey(
        Horario,
        on_delete=models.PROTECT,
        related_name="alocacoes",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PLANEJADA,
    )
    observacao = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = [
            "-periodo_letivo__ano",
            "-periodo_letivo__semestre",
            "horario__dia_semana",
            "horario__horario_inicio",
        ]
        verbose_name = "alocacao"
        verbose_name_plural = "alocacoes"
        constraints = [
            models.UniqueConstraint(
                fields=["periodo_letivo", "sala", "horario"],
                condition=Q(status__in=STATUS_ATIVOS_ALOCACAO),
                name="aloc_sala_horario_sem_conflito",
            ),
            models.UniqueConstraint(
                fields=["periodo_letivo", "professor", "horario"],
                condition=Q(status__in=STATUS_ATIVOS_ALOCACAO),
                name="aloc_prof_horario_sem_conflito",
            ),
            models.UniqueConstraint(
                fields=["periodo_letivo", "turma", "horario"],
                condition=Q(status__in=STATUS_ATIVOS_ALOCACAO),
                name="aloc_turma_horario_sem_conflito",
            ),
        ]
        indexes = [
            models.Index(fields=["periodo_letivo", "status"], name="aloc_periodo_status_idx"),
            models.Index(fields=["periodo_letivo", "sala", "horario"], name="aloc_sala_horario_idx"),
            models.Index(fields=["periodo_letivo", "professor", "horario"], name="aloc_prof_horario_idx"),
            models.Index(fields=["periodo_letivo", "turma", "horario"], name="aloc_turma_horario_idx"),
        ]
