from datetime import date, time

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from alocacao.models import Alocacao, Horario
from academico.models import Curso, Disciplina, PeriodoLetivo
from infraestrutura.models import RecursoSala, Sala
from pessoas.models import DisponibilidadeProfessor, Professor, Turma
from alocacao.repositories.alocacoes import carga_horaria_professor, ocupacao_por_sala
from alocacao.repositories.horarios import horarios_livres_para_turma
from alocacao.repositories.salas import salas_livres
from alocacao.services.alocacoes import cancelar_alocacao, criar_alocacao
from alocacao.services.conflitos import mapear_conflitos


class AlocacaoViewTest(TestCase):
    def test_mensagem_de_erro_aparece_quando_a_alocacao_nao_pode_ser_criada(self):
        response = self.client.post(reverse('alocacao:alocacao_create'), data={})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Erro ao criar alocação!')
        self.assertContains(response, 'alert-danger')


class AlocacaoModelTest(TestCase):
    """testes das regras de banco que evitam conflito na grade."""

    def setUp(self):
        self.periodo_letivo = PeriodoLetivo.objects.create(
            ano=2026,
            semestre=1,
            data_inicio=date(2026, 2, 1),
            data_fim=date(2026, 6, 30),
        )
        self.curso = Curso.objects.create(nome="sistemas de informacao", codigo="si")
        self.professor = Professor.objects.create(
            nome="ana souza",
            email="ana@example.com",
            especialidade="banco de dados",
            carga_horaria_maxima=8,
        )
        self.disciplina = Disciplina.objects.create(
            curso=self.curso,
            nome="banco de dados",
            codigo="bd101",
            carga_horaria_semanal=4,
        )
        self.turma = Turma.objects.create(
            curso=self.curso,
            periodo_letivo=self.periodo_letivo,
            nome="si 1",
            turno=Turma.Turno.NOTURNO,
            numero_alunos=30,
        )
        self.sala = Sala.objects.create(
            nome="sala 101",
            tipo_sala=Sala.TipoSala.COMUM,
            capacidade_alunos=40,
            localizacao="bloco a",
        )
        self.horario = Horario.objects.create(
            dia_semana=Horario.DiaSemana.SEGUNDA,
            horario_inicio=time(19, 0),
            horario_fim=time(21, 0),
        )

    def criar_periodo(self, ano=2026, semestre=2):
        """cria periodo auxiliar para testar recorte por semestre."""

        return PeriodoLetivo.objects.create(
            ano=ano,
            semestre=semestre,
            data_inicio=date(ano, 8, 1),
            data_fim=date(ano, 12, 15),
        )

    def criar_horario(self, inicio, fim):
        """cria outro horario no mesmo dia para testes de carga e conflito."""

        return Horario.objects.create(
            dia_semana=Horario.DiaSemana.SEGUNDA,
            horario_inicio=inicio,
            horario_fim=fim,
        )

    def criar_professor(self, nome="bruno lima", email="bruno@example.com", carga=8):
        """cria professor auxiliar para isolar os cenarios de conflito."""

        return Professor.objects.create(
            nome=nome,
            email=email,
            carga_horaria_maxima=carga,
        )

    def criar_turma(self, nome="si 2", alunos=20, periodo_letivo=None):
        """cria turma auxiliar para nao misturar conflito de turma com outros testes."""

        return Turma.objects.create(
            curso=self.curso,
            periodo_letivo=periodo_letivo or self.periodo_letivo,
            nome=nome,
            turno=Turma.Turno.NOTURNO,
            numero_alunos=alunos,
        )

    def criar_sala(self, nome="sala 102", capacidade=40):
        """cria sala auxiliar para nao misturar conflito de sala com outros testes."""

        return Sala.objects.create(
            nome=nome,
            tipo_sala=Sala.TipoSala.COMUM,
            capacidade_alunos=capacidade,
        )

    def criar_disciplina(self, nome="engenharia de software", codigo="es101", carga=4):
        """cria disciplina auxiliar para testes de carga horaria."""

        return Disciplina.objects.create(
            curso=self.curso,
            nome=nome,
            codigo=codigo,
            carga_horaria_semanal=carga,
        )

    def criar_alocacao(self, **kwargs):
        """cria uma alocacao usando os dados padrao do teste."""

        dados = {
            "periodo_letivo": self.periodo_letivo,
            "professor": self.professor,
            "disciplina": self.disciplina,
            "turma": self.turma,
            "sala": self.sala,
            "horario": self.horario,
        }
        dados.update(kwargs)
        return Alocacao.objects.create(**dados)

    def test_alocacao_valida_salva(self):
        alocacao = self.criar_alocacao()

        self.assertEqual(str(alocacao.disciplina), "bd101 - banco de dados")

    def test_sala_nao_pode_ter_duas_aulas_no_mesmo_horario(self):
        self.criar_alocacao()

        with self.assertRaises(ValidationError):
            self.criar_alocacao(
                professor=self.criar_professor(),
                turma=self.criar_turma(),
            )

    def test_professor_nao_pode_ter_duas_aulas_no_mesmo_horario(self):
        self.criar_alocacao()

        with self.assertRaises(ValidationError):
            self.criar_alocacao(
                turma=self.criar_turma(),
                sala=self.criar_sala(),
            )

    def test_turma_nao_pode_ter_duas_aulas_no_mesmo_horario(self):
        self.criar_alocacao()

        with self.assertRaises(ValidationError):
            self.criar_alocacao(
                professor=self.criar_professor(),
                sala=self.criar_sala(),
            )

    def test_periodos_diferentes_nao_geram_conflito(self):
        self.criar_alocacao()
        outro_periodo = self.criar_periodo()
        outra_turma = self.criar_turma(
            nome="si 1",
            periodo_letivo=outro_periodo,
        )

        alocacao = self.criar_alocacao(
            periodo_letivo=outro_periodo,
            turma=outra_turma,
        )

        self.assertEqual(alocacao.periodo_letivo, outro_periodo)

    def test_periodo_da_alocacao_precisa_ser_o_periodo_da_turma(self):
        outro_periodo = self.criar_periodo()

        with self.assertRaises(ValidationError):
            self.criar_alocacao(periodo_letivo=outro_periodo)

    def test_turma_nao_pode_passar_da_capacidade_da_sala(self):
        with self.assertRaises(ValidationError):
            self.criar_alocacao(sala=self.criar_sala(nome="sala pequena", capacidade=10))

    def test_professor_indisponivel_nao_pode_ser_alocado(self):
        DisponibilidadeProfessor.objects.create(
            professor=self.professor,
            horario=self.horario,
            disponivel=False,
        )

        with self.assertRaises(ValidationError):
            self.criar_alocacao()

    def test_sala_precisa_ter_recurso_exigido_pela_disciplina(self):
        recurso = RecursoSala.objects.create(nome="laboratorio")
        self.disciplina.recursos_necessarios.add(recurso)

        with self.assertRaises(ValidationError):
            self.criar_alocacao()

    def test_professor_nao_pode_estourar_carga_horaria_maxima(self):
        professor = self.criar_professor(
            nome="carla dias",
            email="carla@example.com",
            carga=6,
        )
        self.criar_alocacao(professor=professor)

        with self.assertRaises(ValidationError):
            self.criar_alocacao(
                professor=professor,
                disciplina=self.criar_disciplina(),
                turma=self.criar_turma(),
                sala=self.criar_sala(),
                horario=self.criar_horario(time(21, 0), time(22, 0)),
            )

    def test_alocacao_cancelada_nao_gera_conflito(self):
        self.criar_alocacao(status=Alocacao.Status.CANCELADA)

        alocacao = self.criar_alocacao()

        self.assertEqual(alocacao.status, Alocacao.Status.PLANEJADA)

    def test_horario_fim_precisa_ser_maior_que_inicio(self):
        horario = Horario(
            dia_semana=Horario.DiaSemana.TERCA,
            horario_inicio=time(21, 0),
            horario_fim=time(19, 0),
        )

        with self.assertRaises(ValidationError):
            horario.full_clean()

    def test_service_cria_alocacao_valida(self):
        alocacao = criar_alocacao(
            periodo_letivo=self.periodo_letivo,
            professor=self.professor,
            disciplina=self.disciplina,
            turma=self.turma,
            sala=self.sala,
            horario=self.horario,
        )

        self.assertEqual(alocacao.status, Alocacao.Status.PLANEJADA)

    def test_service_cancela_alocacao(self):
        alocacao = self.criar_alocacao()

        cancelada = cancelar_alocacao(alocacao)

        self.assertEqual(cancelada.status, Alocacao.Status.CANCELADA)

    def test_selector_calcula_carga_horaria_do_professor(self):
        self.criar_alocacao()

        carga = carga_horaria_professor(self.professor, self.periodo_letivo)

        self.assertEqual(carga, 4)

    def test_selector_lista_salas_livres(self):
        self.criar_alocacao()
        sala_livre = self.criar_sala()

        salas = salas_livres(self.periodo_letivo, self.horario)

        self.assertIn(sala_livre, salas)
        self.assertNotIn(self.sala, salas)

    def test_selector_lista_horarios_livres_da_turma(self):
        self.criar_alocacao()
        horario_livre = self.criar_horario(time(21, 0), time(22, 0))

        horarios = horarios_livres_para_turma(self.turma)

        self.assertIn(horario_livre, horarios)
        self.assertNotIn(self.horario, horarios)

    def test_selector_ocupacao_por_sala(self):
        self.criar_alocacao()

        ocupacao = list(ocupacao_por_sala(self.periodo_letivo))

        self.assertEqual(ocupacao[0]["total_alocacoes"], 1)

    def test_service_mapeia_conflitos_sem_salvar(self):
        self.criar_alocacao()
        candidato = Alocacao(
            periodo_letivo=self.periodo_letivo,
            professor=self.criar_professor(),
            disciplina=self.disciplina,
            turma=self.criar_turma(),
            sala=self.sala,
            horario=self.horario,
        )

        conflitos = mapear_conflitos(candidato)

        self.assertIn("sala", conflitos)
