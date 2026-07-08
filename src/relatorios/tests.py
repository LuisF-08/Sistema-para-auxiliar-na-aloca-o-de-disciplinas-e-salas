from datetime import date, time

from django.test import TestCase
from django.urls import reverse

from academico.models import Curso, Disciplina, PeriodoLetivo
from alocacao.models import Alocacao, Horario
from infraestrutura.models import Sala
from pessoas.models import Professor, Turma

from .views import (
    calcular_eficiencia_espaco,
    calcular_horarios_pico,
    calcular_taxa_ocupacao,
    detectar_conflitos_ativos,
)


class RelatoriosBaseTestCase(TestCase):
    """monta um cenario minimo com uma alocacao ativa pra reusar nos testes de relatorio."""

    def setUp(self):
        self.periodo = PeriodoLetivo.objects.create(
            ano=2026, semestre=1,
            data_inicio=date(2026, 2, 1), data_fim=date(2026, 6, 30),
            ativo=True,
        )
        self.curso = Curso.objects.create(nome="sistemas de informacao", codigo="si")
        self.professor = Professor.objects.create(
            nome="ana souza", carga_horaria_maxima=8,
        )
        self.disciplina = Disciplina.objects.create(
            curso=self.curso, nome="banco de dados", codigo="bd101",
            carga_horaria_semanal=4,
        )
        self.turma = Turma.objects.create(
            curso=self.curso, periodo_letivo=self.periodo,
            nome="si 1", turno=Turma.Turno.NOTURNO, numero_alunos=30,
        )
        self.sala = Sala.objects.create(nome="sala 101", capacidade_alunos=40)
        self.horario = Horario.objects.create(
            dia_semana=Horario.DiaSemana.SEGUNDA,
            horario_inicio=time(19, 0), horario_fim=time(21, 0),
        )
        self.alocacao = Alocacao.objects.create(
            periodo_letivo=self.periodo, professor=self.professor,
            disciplina=self.disciplina, turma=self.turma,
            sala=self.sala, horario=self.horario,
        )


class CalcularTaxaOcupacaoTest(RelatoriosBaseTestCase):
    def test_sem_salas_retorna_zero(self):
        # a sala tem uma alocacao protegida (on_delete=PROTECT), entao apaga a alocacao antes
        Alocacao.objects.all().delete()
        Sala.objects.all().delete()

        resultado = calcular_taxa_ocupacao(self.periodo)

        self.assertEqual(resultado["taxa"], 0.0)
        self.assertEqual(resultado["total_salas"], 0)

    def test_uma_sala_ocupada_de_uma_da_100_por_cento(self):
        resultado = calcular_taxa_ocupacao(self.periodo)

        self.assertEqual(resultado["taxa"], 100.0)
        self.assertEqual(resultado["salas_ocupadas"], 1)
        self.assertEqual(resultado["total_salas"], 1)


class CalcularEficienciaEspacoTest(RelatoriosBaseTestCase):
    def test_calcula_assentos_ociosos_da_sala(self):
        resultado = calcular_eficiencia_espaco(self.periodo)

        # sala com 40 lugares, turma com 30 alunos -> 10 assentos ociosos
        self.assertEqual(resultado["media_assentos_ociosos"], 10.0)
        self.assertEqual(len(resultado["detalhe_por_sala"]), 1)

    def test_sem_alocacoes_retorna_zero(self):
        Alocacao.objects.all().delete()

        resultado = calcular_eficiencia_espaco(self.periodo)

        self.assertEqual(resultado["media_assentos_ociosos"], 0.0)
        self.assertEqual(resultado["detalhe_por_sala"], [])


class CalcularHorariosPicoTest(RelatoriosBaseTestCase):
    def test_horario_com_alocacao_aparece_no_ranking(self):
        pico = calcular_horarios_pico(self.periodo)

        self.assertEqual(len(pico), 1)
        self.assertEqual(pico[0]["total_alocacoes"], 1)
        self.assertEqual(pico[0]["dia_nome"], "Segunda-feira")


class DetectarConflitosAtivosTest(RelatoriosBaseTestCase):
    def test_sem_conflitos_retorna_total_zero(self):
        # os indices unicos parciais do banco (ver alocacao.models.Alocacao.Meta)
        # ja impedem duas alocacoes ativas na mesma sala/professor/horario,
        # entao aqui so validamos o caminho feliz (nenhum conflito).
        conflitos = detectar_conflitos_ativos(self.periodo)

        self.assertEqual(conflitos["total"], 0)
        self.assertEqual(conflitos["por_sala"], [])
        self.assertEqual(conflitos["por_professor"], [])


class DashboardViewTest(RelatoriosBaseTestCase):
    def test_dashboard_carrega_com_dados_do_periodo_ativo(self):
        response = self.client.get(reverse("relatorios:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_alocacoes"], 1)
        self.assertEqual(response.context["taxa_ocupacao"], 100.0)


class RelatorioProfessoresViewTest(RelatoriosBaseTestCase):
    def test_lista_professor_com_carga_calculada(self):
        response = self.client.get(reverse("relatorios:professores"))

        self.assertEqual(response.status_code, 200)
        dados = response.context["dados"]
        self.assertEqual(len(dados), 1)
        self.assertEqual(dados[0]["carga_alocada"], 4)
        self.assertEqual(dados[0]["carga_maxima"], 8)


class RelatorioSalasViewTest(RelatoriosBaseTestCase):
    def test_lista_sala_em_uso(self):
        response = self.client.get(reverse("relatorios:salas"))

        self.assertEqual(response.status_code, 200)
        dados = response.context["dados"]
        self.assertEqual(dados[0]["em_uso"], True)


class RelatorioGradeViewTest(RelatoriosBaseTestCase):
    def test_sem_filtro_nao_retorna_alocacoes(self):
        response = self.client.get(reverse("relatorios:grade"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["alocacoes"]), [])

    def test_filtro_por_turma_retorna_alocacao_esperada(self):
        response = self.client.get(reverse("relatorios:grade"), {"turma": self.turma.pk})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["alocacoes"]), [self.alocacao])

    def test_filtro_por_professor_retorna_alocacao_esperada(self):
        response = self.client.get(
            reverse("relatorios:grade"), {"professor": self.professor.pk}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["alocacoes"]), [self.alocacao])


class ExportarCsvTest(RelatoriosBaseTestCase):
    def test_exportacao_csv_contem_a_alocacao(self):
        response = self.client.get(reverse("relatorios:exportar_csv"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response["Content-Type"])
        conteudo = response.content.decode("utf-8-sig")
        self.assertIn("banco de dados", conteudo)
        self.assertIn("ana souza", conteudo)


class ExportarPdfTest(RelatoriosBaseTestCase):
    def test_exportacao_pdf_gera_arquivo(self):
        response = self.client.get(reverse("relatorios:exportar_pdf"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(len(response.content) > 0)
