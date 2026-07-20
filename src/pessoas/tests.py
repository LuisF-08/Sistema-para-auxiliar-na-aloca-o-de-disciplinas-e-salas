from datetime import date, time

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from academico.models import Curso, PeriodoLetivo
from alocacao.models import Horario

from .models import DisponibilidadeProfessor, Professor, Turma


class ProfessorModelTest(TestCase):
    def test_str_mostra_nome(self):
        professor = Professor.objects.create(nome="ana souza", carga_horaria_maxima=8)

        self.assertEqual(str(professor), "ana souza")

    def test_email_precisa_ser_unico_quando_informado(self):
        Professor.objects.create(
            nome="ana souza", email="ana@example.com", carga_horaria_maxima=8,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Professor.objects.create(
                    nome="ana duplicada", email="ana@example.com", carga_horaria_maxima=8,
                )

    def test_email_pode_ficar_em_branco_pra_mais_de_um_professor(self):
        Professor.objects.create(nome="ana souza", carga_horaria_maxima=8)
        professor2 = Professor.objects.create(nome="bruno lima", carga_horaria_maxima=6)

        self.assertIsNone(professor2.email)

    def test_carga_horaria_maxima_minima_e_validada_no_full_clean(self):
        professor = Professor(nome="sem carga", carga_horaria_maxima=0)

        with self.assertRaises(ValidationError):
            professor.full_clean()


class TurmaModelTest(TestCase):
    def setUp(self):
        self.curso = Curso.objects.create(nome="sistemas de informacao", codigo="si")
        self.periodo = PeriodoLetivo.objects.create(
            ano=2026, semestre=1,
            data_inicio=date(2026, 2, 1), data_fim=date(2026, 6, 30),
        )

    def test_str_mostra_nome_curso_e_periodo(self):
        turma = Turma.objects.create(
            curso=self.curso, periodo_letivo=self.periodo,
            nome="si 1", turno=Turma.Turno.NOTURNO, numero_alunos=30,
        )

        self.assertEqual(str(turma), "si 1 - si (2026.1)")

    def test_nome_repetido_no_mesmo_curso_e_periodo_da_erro(self):
        Turma.objects.create(
            curso=self.curso, periodo_letivo=self.periodo,
            nome="si 1", turno=Turma.Turno.NOTURNO, numero_alunos=30,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Turma.objects.create(
                    curso=self.curso, periodo_letivo=self.periodo,
                    nome="si 1", turno=Turma.Turno.MATUTINO, numero_alunos=20,
                )

    def test_mesmo_nome_em_periodo_diferente_e_permitido(self):
        outro_periodo = PeriodoLetivo.objects.create(
            ano=2026, semestre=2,
            data_inicio=date(2026, 8, 1), data_fim=date(2026, 12, 15),
        )
        Turma.objects.create(
            curso=self.curso, periodo_letivo=self.periodo,
            nome="si 1", turno=Turma.Turno.NOTURNO, numero_alunos=30,
        )

        turma2 = Turma.objects.create(
            curso=self.curso, periodo_letivo=outro_periodo,
            nome="si 1", turno=Turma.Turno.NOTURNO, numero_alunos=25,
        )

        self.assertEqual(turma2.nome, "si 1")


class DisponibilidadeProfessorModelTest(TestCase):
    def setUp(self):
        self.professor = Professor.objects.create(nome="ana souza", carga_horaria_maxima=8)
        self.horario = Horario.objects.create(
            dia_semana=Horario.DiaSemana.SEGUNDA,
            horario_inicio=time(19, 0), horario_fim=time(21, 0),
        )

    def test_str_mostra_status_disponivel(self):
        disponibilidade = DisponibilidadeProfessor.objects.create(
            professor=self.professor, horario=self.horario, disponivel=True,
        )

        self.assertIn("disponivel", str(disponibilidade))

    def test_professor_so_pode_ter_um_registro_por_horario(self):
        DisponibilidadeProfessor.objects.create(
            professor=self.professor, horario=self.horario, disponivel=False,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                DisponibilidadeProfessor.objects.create(
                    professor=self.professor, horario=self.horario, disponivel=True,
                )

    def test_deletar_professor_apaga_disponibilidade_em_cascade(self):
        DisponibilidadeProfessor.objects.create(
            professor=self.professor, horario=self.horario, disponivel=False,
        )

        self.professor.delete()

        self.assertEqual(DisponibilidadeProfessor.objects.count(), 0)


class ProfessorViewsTest(TestCase):
    """cobre a view de listagem que quebrava por falta do import de render."""

    def test_lista_professores_carrega_sem_erro(self):
        Professor.objects.create(nome="ana souza", carga_horaria_maxima=8)

        response = self.client.get(reverse("pessoas:professor_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ana souza")

    def test_lista_professores_vazia_nao_quebra(self):
        response = self.client.get(reverse("pessoas:professor_list"))

        self.assertEqual(response.status_code, 200)

    def test_criar_professor_via_post(self):
        response = self.client.post(reverse("pessoas:professor_create"), {
            "nome": "carla dias",
            "carga_horaria_maxima": 6,
            "ativo": True,
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Professor.objects.filter(nome="carla dias").exists())
