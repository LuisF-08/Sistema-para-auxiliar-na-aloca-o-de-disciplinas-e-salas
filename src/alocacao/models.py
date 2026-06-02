from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q, Sum


STATUS_ATIVOS_ALOCACAO = ["planejada", "confirmada"]


class TimeStampedModel(models.Model):
    """guarda quando o registro foi criado e alterado."""

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Curso(TimeStampedModel):
    """curso que agrupa disciplinas e turmas."""

    nome = models.CharField(max_length=120, unique=True)
    codigo = models.CharField(max_length=20, unique=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "curso"
        verbose_name_plural = "cursos"

    def __str__(self):
        return f"{self.codigo} - {self.nome}"


class PeriodoLetivo(TimeStampedModel):
    """recorta a grade por ano e semestre, evitando conflito entre periodos."""

    ano = models.PositiveSmallIntegerField(validators=[MinValueValidator(2000)])
    semestre = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        help_text="use 1 ou 2 para semestre regular.",
    )
    data_inicio = models.DateField()
    data_fim = models.DateField()
    ativo = models.BooleanField(default=True)

    class Meta:
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

    def __str__(self):
        return f"{self.ano}.{self.semestre}"


class Professor(TimeStampedModel):
    """docente e seu limite semanal de horas/aula."""

    nome = models.CharField(max_length=120)
    email = models.EmailField(unique=True, blank=True, null=True)
    especialidade = models.CharField(max_length=120, blank=True)
    carga_horaria_maxima = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        help_text="limite semanal de horas/aula do professor.",
    )
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "professor"
        verbose_name_plural = "professores"
        indexes = [
            models.Index(fields=["nome"], name="professor_nome_idx"),
        ]

    def __str__(self):
        return self.nome


class RecursoSala(TimeStampedModel):
    """recurso fisico ou tecnologico que pode existir em uma sala."""

    nome = models.CharField(max_length=80, unique=True)
    descricao = models.TextField(blank=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "recurso de sala"
        verbose_name_plural = "recursos de sala"

    def __str__(self):
        return self.nome


class Disciplina(TimeStampedModel):
    """disciplina ofertada por um curso, com sua carga horaria semanal."""

    curso = models.ForeignKey(
        Curso,
        on_delete=models.PROTECT,
        related_name="disciplinas",
    )
    nome = models.CharField(max_length=120)
    codigo = models.CharField(max_length=30)
    carga_horaria_semanal = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        help_text="quantidade de horas/aula por semana.",
    )
    periodo_recomendado = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text="periodo/semestre ideal da grade, se existir.",
    )
    recursos_necessarios = models.ManyToManyField(
        RecursoSala,
        blank=True,
        related_name="disciplinas",
    )
    ativo = models.BooleanField(default=True)

    class Meta:
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


class Turma(TimeStampedModel):
    """grupo de alunos dentro de um curso e periodo letivo."""

    class Turno(models.TextChoices):
        MATUTINO = "matutino", "matutino"
        VESPERTINO = "vespertino", "vespertino"
        NOTURNO = "noturno", "noturno"
        INTEGRAL = "integral", "integral"

    curso = models.ForeignKey(
        Curso,
        on_delete=models.PROTECT,
        related_name="turmas",
    )
    periodo_letivo = models.ForeignKey(
        PeriodoLetivo,
        on_delete=models.PROTECT,
        related_name="turmas",
    )
    nome = models.CharField(max_length=80)
    turno = models.CharField(max_length=20, choices=Turno.choices)
    numero_alunos = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
    )
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = [
            "-periodo_letivo__ano",
            "-periodo_letivo__semestre",
            "curso__nome",
            "nome",
        ]
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


class Sala(TimeStampedModel):
    """ambiente fisico usado para receber aulas."""

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


class Horario(TimeStampedModel):
    """faixa de horario usada para montar a grade semanal."""

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


class DisponibilidadeProfessor(TimeStampedModel):
    """indica se o professor pode ou n lecionar em um horario."""

    professor = models.ForeignKey(
        Professor,
        on_delete=models.CASCADE,
        related_name="disponibilidades",
    )
    horario = models.ForeignKey(
        Horario,
        on_delete=models.CASCADE,
        related_name="disponibilidades_professores",
    )
    disponivel = models.BooleanField(default=True)
    observacao = models.CharField(max_length=160, blank=True)

    class Meta:
        ordering = ["professor__nome", "horario__dia_semana", "horario__horario_inicio"]
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


class Alocacao(TimeStampedModel):
    """liga professor, disciplina, turma, sala e horario em uma aula."""

    class Status(models.TextChoices):
        PLANEJADA = "planejada", "planejada"
        CONFIRMADA = "confirmada", "confirmada"
        CANCELADA = "cancelada", "cancelada"

    periodo_letivo = models.ForeignKey(
        PeriodoLetivo,
        on_delete=models.PROTECT,
        related_name="alocacoes",
    )
    professor = models.ForeignKey(
        Professor,
        on_delete=models.PROTECT,
        related_name="alocacoes",
    )
    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.PROTECT,
        related_name="alocacoes",
    )
    turma = models.ForeignKey(
        Turma,
        on_delete=models.PROTECT,
        related_name="alocacoes",
    )
    sala = models.ForeignKey(
        Sala,
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

    class Meta:
        ordering = [
            "-periodo_letivo__ano",
            "-periodo_letivo__semestre",
            "horario__dia_semana",
            "horario__horario_inicio",
            "sala__nome",
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

    @property
    def ativa_para_grade(self):
        """retorna s quando a alocacao ainda conta para conflitos e relatorios."""

        return self.status in set(STATUS_ATIVOS_ALOCACAO)

    def clean(self):
        """valida regras que dependem de mais de uma tabela."""

        super().clean()

        if self.status == self.Status.CANCELADA:
            return

        erros = {}
        self._validar_entidades_ativas(erros)
        self._validar_periodo_da_turma(erros)
        self._validar_capacidade_sala(erros)
        self._validar_conflitos_de_horario(erros)
        self._validar_disponibilidade_professor(erros)
        self._validar_recursos_da_sala(erros)
        self._validar_carga_horaria_professor(erros)

        if erros:
            raise ValidationError(erros)

    def save(self, *args, **kwargs):
        """sempre valida antes de salvar para n depender so da tela/admin."""

        self.full_clean()
        return super().save(*args, **kwargs)

    def _validar_entidades_ativas(self, erros):
        """evita usar cadastros inativos em uma alocacao ativa."""

        entidades = {
            "periodo_letivo": self.periodo_letivo if self.periodo_letivo_id else None,
            "professor": self.professor if self.professor_id else None,
            "disciplina": self.disciplina if self.disciplina_id else None,
            "turma": self.turma if self.turma_id else None,
            "sala": self.sala if self.sala_id else None,
            "horario": self.horario if self.horario_id else None,
        }

        for campo, entidade in entidades.items():
            if entidade and hasattr(entidade, "ativo") and not entidade.ativo:
                erros[campo] = f"{campo} inativo n pode ser usado na alocacao."

    def _validar_periodo_da_turma(self, erros):
        """garante que a alocacao usa o mesmo periodo da turma."""

        if self.periodo_letivo_id and self.turma_id:
            if self.turma.periodo_letivo_id != self.periodo_letivo_id:
                erros["periodo_letivo"] = "o periodo da alocacao precisa ser o periodo da turma."

    def _validar_capacidade_sala(self, erros):
        """garante que a turma cabe na sala escolhida."""

        if self.sala_id and self.turma_id:
            if self.turma.numero_alunos > self.sala.capacidade_alunos:
                erros["sala"] = (
                    "a sala n comporta essa turma, pq a quantidade de alunos "
                    "passa da capacidade cadastrada."
                )

    def _validar_conflitos_de_horario(self, erros):
        """bloqueia choque de sala, professor ou turma no mesmo periodo/horario."""

        if not self.periodo_letivo_id or not self.horario_id:
            return

        alocacoes = Alocacao.objects.filter(
            periodo_letivo=self.periodo_letivo,
            horario=self.horario,
            status__in=STATUS_ATIVOS_ALOCACAO,
        ).exclude(pk=self.pk)

        if self.sala_id and alocacoes.filter(sala=self.sala).exists():
            erros["sala"] = "essa sala ja possui aula nesse periodo e horario."

        if self.professor_id and alocacoes.filter(professor=self.professor).exists():
            erros["professor"] = "esse professor ja possui aula nesse periodo e horario."

        if self.turma_id and alocacoes.filter(turma=self.turma).exists():
            erros["turma"] = "essa turma ja possui aula nesse periodo e horario."

    def _validar_disponibilidade_professor(self, erros):
        """respeita bloqueios de disponibilidade cadastrados para o professor."""

        if not self.professor_id or not self.horario_id:
            return

        disponibilidade = DisponibilidadeProfessor.objects.filter(
            professor=self.professor,
            horario=self.horario,
        ).first()

        if disponibilidade and not disponibilidade.disponivel:
            erros["professor"] = "o professor esta marcado como indisponivel nesse horario."

    def _validar_recursos_da_sala(self, erros):
        """confere se a sala tem os recursos exigidos pela disciplina."""

        if not self.disciplina_id or not self.sala_id:
            return

        recursos_necessarios = set(
            self.disciplina.recursos_necessarios.values_list("id", flat=True)
        )
        if not recursos_necessarios:
            return

        recursos_sala = set(self.sala.recursos.values_list("id", flat=True))
        recursos_faltando = recursos_necessarios - recursos_sala

        if recursos_faltando:
            nomes = RecursoSala.objects.filter(id__in=recursos_faltando).values_list(
                "nome",
                flat=True,
            )
            erros["sala"] = (
                "a sala n possui todos os recursos necessarios: "
                + ", ".join(sorted(nomes))
            )

    def _validar_carga_horaria_professor(self, erros):
        """confere se a nova alocacao estoura a carga semanal do professor."""

        if not self.periodo_letivo_id or not self.professor_id or not self.disciplina_id:
            return

        carga_atual = (
            Alocacao.objects.filter(
                periodo_letivo=self.periodo_letivo,
                professor=self.professor,
                status__in=STATUS_ATIVOS_ALOCACAO,
            )
            .exclude(pk=self.pk)
            .aggregate(total=Sum("disciplina__carga_horaria_semanal"))
            .get("total")
            or 0
        )
        carga_total = carga_atual + self.disciplina.carga_horaria_semanal

        if carga_total > self.professor.carga_horaria_maxima:
            erros["professor"] = (
                "essa alocacao estoura a carga horaria maxima semanal do professor."
            )

    def __str__(self):
        return (
            f"{self.periodo_letivo} | {self.disciplina} | {self.turma} | "
            f"{self.sala} | {self.horario}"
        )
