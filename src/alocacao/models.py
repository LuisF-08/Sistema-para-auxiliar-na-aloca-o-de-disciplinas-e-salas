from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q, Sum  
from django.apps import apps


STATUS_ATIVOS_ALOCACAO = ["planejada", "confirmada"]


class Horario(models.Model):
    class DiaSemana(models.TextChoices):
        SEGUNDA = '1', 'Segunda-feira'
        TERCA = '2', 'Terça-feira'
        QUARTA = '3', 'Quarta-feira'
        QUINTA = '4', 'Quinta-feira'
        SEXTA = '5', 'Sexta-feira'
        SABADO = '6', 'Sábado'

    dia_semana = models.CharField(
        max_length=1,
        choices=DiaSemana.choices
    )
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["dia_semana", "horario_inicio"]
        verbose_name = "horário"
        verbose_name_plural = "horários"
        constraints = [
            models.UniqueConstraint(
                fields=["dia_semana", "horario_inicio", "horario_fim"],
                name="horario_faixa_unica"
            )
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
        indexes = [
            models.Index(fields=["periodo_letivo", "status"], name="aloc_periodo_status_idx"),
            models.Index(fields=["periodo_letivo", "sala", "horario"], name="aloc_sala_horario_idx"),
            models.Index(fields=["periodo_letivo", "professor", "horario"], name="aloc_prof_horario_idx"),
            models.Index(fields=["periodo_letivo", "turma", "horario"], name="aloc_turma_horario_idx"),
        ]

    def __str__(self):
        try:
            return (
            f"{self.disciplina} | {self.turma} | "
            f"{self.sala} | {self.horario} [{self.status}]"
        )
        except Exception:
            return f"alocacao #{self.pk or 'nova'} [{self.status}]"

    def clean(self):
        """Apenas valida dados estruturais básicos (como período letivo), permitindo conflitos operacionais para exibição na tela de auditoria."""
        if self.status == self.Status.CANCELADA:
            return
        erros = {}

        if (
            self.periodo_letivo_id
            and self.turma_id
            and self.turma.periodo_letivo_id != self.periodo_letivo_id
        ):
            erros["periodo_letivo"] = [
                "o periodo letivo informado e diferente do periodo da turma."
            ]

        if erros:
            raise ValidationError(erros)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)