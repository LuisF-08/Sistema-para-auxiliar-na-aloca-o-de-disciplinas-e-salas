from django.core.validators import MinValueValidator
from django.db import models


class Professor(models.Model):
    nome = models.CharField(max_length=120)
    email = models.EmailField(unique=True, blank=True, null=True)
    especialidade = models.CharField(max_length=120, blank=True)
    carga_horaria_maxima = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
    )
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "professor"
        verbose_name_plural = "professores"
        indexes = [
            models.Index(fields=["nome"], name="professor_nome_idx"),
        ]

    def __str__(self):
        return self.nome


class Turma(models.Model):
    class Turno(models.TextChoices):
        MATUTINO = "matutino", "matutino"
        VESPERTINO = "vespertino", "vespertino"
        NOTURNO = "noturno", "noturno"
        INTEGRAL = "integral", "integral"

    curso = models.ForeignKey(
        "academico.Curso",
        on_delete=models.PROTECT,
        related_name="turmas",
    )
    periodo_letivo = models.ForeignKey(
        "academico.PeriodoLetivo",
        on_delete=models.PROTECT,
        related_name="turmas",
    )
    nome = models.CharField(max_length=80)
    turno = models.CharField(max_length=20, choices=Turno.choices)
    numero_alunos = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
    )
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-periodo_letivo__ano", "-periodo_letivo__semestre", "nome"]
        verbose_name = "turma"
        verbose_name_plural = "turmas"
        constraints = [
            models.UniqueConstraint(
                fields=["curso", "periodo_letivo", "nome"],
                name="turma_unica_por_periodo",
            ),
        ]
        indexes = [
            models.Index(fields=["periodo_letivo"], name="turma_periodo_idx"),
            models.Index(fields=["curso", "periodo_letivo"], name="turma_curso_periodo_idx"),
        ]

    def __str__(self):
        return f"{self.nome} - {self.curso.codigo} ({self.periodo_letivo})"


class DisponibilidadeProfessor(models.Model):
    professor = models.ForeignKey(
        Professor,
        on_delete=models.CASCADE,
        related_name="disponibilidades",
    )
    horario = models.ForeignKey(
        "alocacao.Horario",
        on_delete=models.CASCADE,
        related_name="disponibilidades_professores",
    )
    disponivel = models.BooleanField(default=True)
    observacao = models.CharField(max_length=160, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["professor__nome", "horario__dia_semana"]
        verbose_name = "disponibilidade do professor"
        verbose_name_plural = "disponibilidades dos professores"
        constraints = [
            models.UniqueConstraint(
                fields=["professor", "horario"],
                name="disponibilidade_unica_por_professor_horario",
            ),
        ]

    def __str__(self):
        status = "disponivel" if self.disponivel else "indisponivel"
        return f"{self.professor} - {self.horario} ({status})"