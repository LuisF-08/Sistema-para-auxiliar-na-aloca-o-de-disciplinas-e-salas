from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q, Sum  # sum e usado no clean() para calcular carga horaria


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

    def __str__(self):
        return f"alocacao #{self.pk or 'nova'} [{self.status}]"

    def clean(self):
        """valida regras de negocio que o banco nao consegue checar sozinho."""
        # pessoas.models so e importado aqui para evitar importacao circular no nivel do modulo
        from pessoas.models import DisponibilidadeProfessor

        erros = {}

        # o periodo letivo da turma precisa ser o mesmo da alocacao
        if (
            self.periodo_letivo_id
            and self.turma_id
            and self.turma.periodo_letivo_id != self.periodo_letivo_id
        ):
            erros["periodo_letivo"] = [
                "o periodo letivo informado e diferente do periodo da turma."
            ]

        # as validacoes abaixo so se aplicam a alocacoes que geram ocupacao real
        if self.status in STATUS_ATIVOS_ALOCACAO:
            erros_sala = []
            erros_professor = []

            # numero de alunos da turma nao pode superar a capacidade da sala
            if self.turma_id and self.sala_id:
                if self.turma.numero_alunos > self.sala.capacidade_alunos:
                    erros_sala.append(
                        f"a turma tem {self.turma.numero_alunos} alunos, "
                        f"mas a sala comporta apenas {self.sala.capacidade_alunos}."
                    )

            # sala nao pode ter duas aulas ativas no mesmo periodo/horario
            if self.sala_id and self.horario_id and self.periodo_letivo_id:
                qs = Alocacao.objects.filter(
                    sala_id=self.sala_id,
                    horario_id=self.horario_id,
                    periodo_letivo_id=self.periodo_letivo_id,
                    status__in=STATUS_ATIVOS_ALOCACAO,
                )
                if self.pk:
                    qs = qs.exclude(pk=self.pk)
                if qs.exists():
                    erros_sala.append(
                        "a sala ja possui uma aula ativa neste horario e periodo."
                    )

            # professor nao pode estar marcado como indisponivel neste horario
            if self.professor_id and self.horario_id:
                if DisponibilidadeProfessor.objects.filter(
                    professor_id=self.professor_id,
                    horario_id=self.horario_id,
                    disponivel=False,
                ).exists():
                    erros_professor.append(
                        "o professor esta marcado como indisponivel neste horario."
                    )

            # professor nao pode ter duas aulas ativas no mesmo periodo/horario
            if self.professor_id and self.horario_id and self.periodo_letivo_id:
                qs = Alocacao.objects.filter(
                    professor_id=self.professor_id,
                    horario_id=self.horario_id,
                    periodo_letivo_id=self.periodo_letivo_id,
                    status__in=STATUS_ATIVOS_ALOCACAO,
                )
                if self.pk:
                    qs = qs.exclude(pk=self.pk)
                if qs.exists():
                    erros_professor.append(
                        "o professor ja possui uma aula ativa neste horario e periodo."
                    )

            # turma nao pode ter duas aulas ativas no mesmo periodo/horario
            if self.turma_id and self.horario_id and self.periodo_letivo_id:
                qs = Alocacao.objects.filter(
                    turma_id=self.turma_id,
                    horario_id=self.horario_id,
                    periodo_letivo_id=self.periodo_letivo_id,
                    status__in=STATUS_ATIVOS_ALOCACAO,
                )
                if self.pk:
                    qs = qs.exclude(pk=self.pk)
                if qs.exists():
                    erros["turma"] = [
                        "a turma ja possui uma aula ativa neste horario e periodo."
                    ]

            # sala precisa possuir todos os recursos exigidos pela disciplina
            if self.disciplina_id and self.sala_id:
                ids_exigidos = set(
                    self.disciplina.recursos_necessarios.values_list("id", flat=True)
                )
                if ids_exigidos:
                    ids_sala = set(self.sala.recursos.values_list("id", flat=True))
                    ids_faltantes = ids_exigidos - ids_sala
                    if ids_faltantes:
                        nomes = ", ".join(
                            self.disciplina.recursos_necessarios
                            .filter(id__in=ids_faltantes)
                            .values_list("nome", flat=True)
                        )
                        erros_sala.append(
                            f"a sala nao possui os recursos exigidos: {nomes}."
                        )

            # professor nao pode ultrapassar a carga horaria maxima no periodo
            if self.professor_id and self.disciplina_id and self.periodo_letivo_id:
                qs = Alocacao.objects.filter(
                    professor_id=self.professor_id,
                    periodo_letivo_id=self.periodo_letivo_id,
                    status__in=STATUS_ATIVOS_ALOCACAO,
                )
                # ao editar, descontar a propria linha para nao contar em duplicata
                if self.pk:
                    qs = qs.exclude(pk=self.pk)
                carga_atual = (
                    qs.aggregate(total=Sum("disciplina__carga_horaria_semanal"))
                    .get("total") or 0
                )
                nova_carga = self.disciplina.carga_horaria_semanal
                if carga_atual + nova_carga > self.professor.carga_horaria_maxima:
                    erros_professor.append(
                        f"professor ja acumula {carga_atual}h no periodo; "
                        f"adicionar {nova_carga}h ultrapassaria o limite de "
                        f"{self.professor.carga_horaria_maxima}h/semana."
                    )

            if erros_sala:
                erros["sala"] = erros_sala
            if erros_professor:
                erros["professor"] = erros_professor

        if erros:
            raise ValidationError(erros)

    def save(self, *args, **kwargs):
        """garante que as regras de negocio sao sempre validadas antes de salvar."""
        self.full_clean()
        super().save(*args, **kwargs)
