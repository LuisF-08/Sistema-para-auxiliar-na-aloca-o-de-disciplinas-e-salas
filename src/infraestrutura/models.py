from django.core.validators import MinValueValidator
from django.db import models


class RecursoSala(models.Model):
    nome = models.CharField(max_length=80, unique=True)
    descricao = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "recurso de sala"
        verbose_name_plural = "recursos de sala"

    def __str__(self):
        return self.nome


class Sala(models.Model):
    class TipoSala(models.TextChoices):
        COMUM = "comum", "comum"
        LABORATORIO = "laboratorio", "laboratorio"
        AUDITORIO = "auditorio", "auditorio"
        ONLINE = "online", "online"

    nome = models.CharField(max_length=80, unique=True)
    tipo_sala = models.CharField(
        max_length=20,
        choices=TipoSala.choices,
        default=TipoSala.COMUM,
    )
    capacidade_alunos = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
    )
    localizacao = models.CharField(max_length=120, blank=True)
    recursos = models.ManyToManyField(
        RecursoSala,
        blank=True,
        related_name="salas",
    )
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "sala"
        verbose_name_plural = "salas"
        indexes = [
            models.Index(fields=["tipo_sala"], name="sala_tipo_idx"),
            models.Index(fields=["capacidade_alunos"], name="sala_capacidade_idx"),
        ]

    def __str__(self):
        return f"{self.nome} ({self.capacidade_alunos} alunos)"