from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class TimeStampedModel(models.Model):
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
    


class Curso(TimeStampedModel):
    nome = models.CharField(max_length=120, unique=True)
    codigo = models.CharField(max_length=20, unique=True)
    ativo = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        ordering = ["nome"]
        verbose_name = "curso"
        verbose_name_plural = "cursos"

    def __str__(self):
        return f"{self.codigo} - {self.nome}"


class PeriodoLetivo(TimeStampedModel):
    ano = models.PositiveSmallIntegerField(validators=[MinValueValidator(2000)])
    semestre = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        help_text="use 1 ou 2 para semestre regular.",
    )
    data_inicio = models.DateField()
    data_fim = models.DateField()
    ativo = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        ordering = ["-ano", "-semestre"]
        verbose_name = "periodo letivo"
        verbose_name_plural = "periodos letivos"
        constraints = [
            models.CheckConstraint(
                condition=Q(semestre__in=[1, 2]),
                name="periodo_letivo_semestre_valido",
            ),
            models.CheckConstraint(
                condition=Q(data_fim__gt=models.F("data_inicio")),
                name="periodo_letivo_datas_validas",
            ),
            models.UniqueConstraint(
                fields=["ano", "semestre"],
                name="periodo_letivo_unico",
            ),
        ]
        indexes = [
            models.Index(fields=["ano", "semestre"], name="periodo_letivo_idx"),
        ]

    @classmethod
    def atual(cls):
        # retorna o periodo letivo corrente: o mais recente entre os ativos.
        return cls.objects.filter(ativo=True).first()

    def __str__(self):
        return f"{self.ano}.{self.semestre}"


class Disciplina(TimeStampedModel):
    curso = models.ForeignKey(
        "academico.Curso",
        on_delete=models.PROTECT,
        related_name="disciplinas",
    )
    nome = models.CharField(max_length=120)
    codigo = models.CharField(max_length=30)
    carga_horaria_semanal = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
    )
    periodo_recomendado = models.PositiveSmallIntegerField(
        blank=True, null=True,
        validators=[MinValueValidator(1)],
    )
    recursos_necessarios = models.ManyToManyField(
        "infraestrutura.RecursoSala",
        blank=True,
        related_name="disciplinas",
    )
    ativo = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        ordering = ["curso__nome", "nome"]
        verbose_name = "disciplina"
        verbose_name_plural = "disciplinas"
        constraints = [
            models.UniqueConstraint(
                fields=["curso", "codigo"],
                name="disciplina_codigo_unico_por_curso",
            ),
            models.UniqueConstraint(
                fields=["curso", "nome"],
                name="disciplina_nome_unico_por_curso",
            ),
        ]
        indexes = [
            models.Index(fields=["codigo"], name="disciplina_codigo_idx"),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.nome}"
    
    