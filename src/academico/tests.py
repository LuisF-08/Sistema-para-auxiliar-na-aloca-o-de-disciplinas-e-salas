from datetime import date

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from .models import Curso, Disciplina, PeriodoLetivo


class CursoModelTest(TestCase):
    def test_str_mostra_codigo_e_nome(self):
        curso = Curso.objects.create(nome="sistemas de informacao", codigo="si")

        self.assertEqual(str(curso), "si - sistemas de informacao")

    def test_nome_precisa_ser_unico(self):
        Curso.objects.create(nome="sistemas de informacao", codigo="si")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Curso.objects.create(nome="sistemas de informacao", codigo="si2")

    def test_codigo_precisa_ser_unico(self):
        Curso.objects.create(nome="sistemas de informacao", codigo="si")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Curso.objects.create(nome="outro curso", codigo="si")


class PeriodoLetivoModelTest(TestCase):
    def test_str_mostra_ano_ponto_semestre(self):
        periodo = PeriodoLetivo.objects.create(
            ano=2026, semestre=1,
            data_inicio=date(2026, 2, 1), data_fim=date(2026, 6, 30),
        )

        self.assertEqual(str(periodo), "2026.1")

    def test_semestre_so_pode_ser_1_ou_2(self):
        # constraint e no banco (CheckConstraint), n no clean() python
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                PeriodoLetivo.objects.create(
                    ano=2026, semestre=3,
                    data_inicio=date(2026, 2, 1), data_fim=date(2026, 6, 30),
                )

    def test_data_fim_precisa_ser_maior_que_data_inicio(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                PeriodoLetivo.objects.create(
                    ano=2026, semestre=1,
                    data_inicio=date(2026, 6, 30), data_fim=date(2026, 2, 1),
                )

    def test_ano_e_semestre_precisam_ser_unicos_juntos(self):
        PeriodoLetivo.objects.create(
            ano=2026, semestre=1,
            data_inicio=date(2026, 2, 1), data_fim=date(2026, 6, 30),
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                PeriodoLetivo.objects.create(
                    ano=2026, semestre=1,
                    data_inicio=date(2026, 3, 1), data_fim=date(2026, 7, 30),
                )


class DisciplinaModelTest(TestCase):
    def setUp(self):
        self.curso = Curso.objects.create(nome="sistemas de informacao", codigo="si")
        self.outro_curso = Curso.objects.create(nome="ciencia da computacao", codigo="cc")

    def test_str_mostra_codigo_e_nome(self):
        disciplina = Disciplina.objects.create(
            curso=self.curso, nome="banco de dados", codigo="bd101",
            carga_horaria_semanal=4,
        )

        self.assertEqual(str(disciplina), "bd101 - banco de dados")

    def test_codigo_repetido_no_mesmo_curso_da_erro(self):
        Disciplina.objects.create(
            curso=self.curso, nome="banco de dados", codigo="bd101",
            carga_horaria_semanal=4,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Disciplina.objects.create(
                    curso=self.curso, nome="outra materia", codigo="bd101",
                    carga_horaria_semanal=2,
                )

    def test_mesmo_codigo_em_cursos_diferentes_e_permitido(self):
        Disciplina.objects.create(
            curso=self.curso, nome="banco de dados", codigo="bd101",
            carga_horaria_semanal=4,
        )

        disciplina2 = Disciplina.objects.create(
            curso=self.outro_curso, nome="banco de dados avancado", codigo="bd101",
            carga_horaria_semanal=4,
        )

        self.assertEqual(disciplina2.codigo, "bd101")

    def test_carga_horaria_minima_e_validada_no_full_clean(self):
        disciplina = Disciplina(
            curso=self.curso, nome="materia invalida", codigo="mi01",
            carga_horaria_semanal=0,
        )

        with self.assertRaises(ValidationError):
            disciplina.full_clean()


class DisciplinaListViewTest(TestCase):
    def test_lista_disciplinas_cadastradas(self):
        curso = Curso.objects.create(nome="sistemas de informacao", codigo="si")
        Disciplina.objects.create(
            curso=curso, nome="banco de dados", codigo="bd101",
            carga_horaria_semanal=4,
        )

        response = self.client.get(reverse("academico:disciplina_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "banco de dados")
