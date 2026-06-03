from datetime import date, time

from django.core.management.base import BaseCommand
from django.db import transaction

from alocacao.models import (
    Alocacao,
    Curso,
    Disciplina,
    DisponibilidadeProfessor,
    Horario,
    PeriodoLetivo,
    Professor,
    RecursoSala,
    Sala,
    Turma,
)
from alocacao.services.alocacoes import criar_alocacao


class Command(BaseCommand):
    help = "cria dados simulados para testar banco, admin, dashboard e relatorios"

    def handle(self, *args, **options):
        with transaction.atomic():
            dados = self._criar_base()
            self._criar_disponibilidades(dados)
            total = self._criar_alocacoes(dados)

        self.stdout.write(
            self.style.SUCCESS(
                f"seed concluido com sucesso. {total} alocacao(oes) pronta(s)."
            )
        )

    def _criar_base(self):
        """cria os cadastros principais sem duplicar dados."""

        periodo, _ = PeriodoLetivo.objects.get_or_create(
            ano=2026,
            semestre=1,
            defaults={
                "data_inicio": date(2026, 2, 1),
                "data_fim": date(2026, 6, 30),
            },
        )
        curso, _ = Curso.objects.get_or_create(
            codigo="si",
            defaults={"nome": "sistemas de informacao"},
        )

        projetor, _ = RecursoSala.objects.get_or_create(nome="projetor")
        laboratorio, _ = RecursoSala.objects.get_or_create(nome="laboratorio")

        professores = {
            "ana": Professor.objects.get_or_create(
                email="ana.souza@example.com",
                defaults={
                    "nome": "ana souza",
                    "especialidade": "banco de dados",
                    "carga_horaria_maxima": 12,
                },
            )[0],
            "bruno": Professor.objects.get_or_create(
                email="bruno.lima@example.com",
                defaults={
                    "nome": "bruno lima",
                    "especialidade": "engenharia de software",
                    "carga_horaria_maxima": 10,
                },
            )[0],
            "carla": Professor.objects.get_or_create(
                email="carla.dias@example.com",
                defaults={
                    "nome": "carla dias",
                    "especialidade": "programacao",
                    "carga_horaria_maxima": 10,
                },
            )[0],
        }

        disciplinas = {
            "bd": Disciplina.objects.get_or_create(
                curso=curso,
                codigo="bd101",
                defaults={
                    "nome": "banco de dados",
                    "carga_horaria_semanal": 4,
                    "periodo_recomendado": 3,
                },
            )[0],
            "es": Disciplina.objects.get_or_create(
                curso=curso,
                codigo="es101",
                defaults={
                    "nome": "engenharia de software",
                    "carga_horaria_semanal": 4,
                    "periodo_recomendado": 4,
                },
            )[0],
            "lp": Disciplina.objects.get_or_create(
                curso=curso,
                codigo="lp101",
                defaults={
                    "nome": "logica de programacao",
                    "carga_horaria_semanal": 4,
                    "periodo_recomendado": 1,
                },
            )[0],
        }
        disciplinas["bd"].recursos_necessarios.add(projetor)
        disciplinas["lp"].recursos_necessarios.add(laboratorio)

        turmas = {
            "si1": Turma.objects.get_or_create(
                curso=curso,
                periodo_letivo=periodo,
                nome="si 1",
                defaults={"turno": Turma.Turno.NOTURNO, "numero_alunos": 35},
            )[0],
            "si2": Turma.objects.get_or_create(
                curso=curso,
                periodo_letivo=periodo,
                nome="si 2",
                defaults={"turno": Turma.Turno.NOTURNO, "numero_alunos": 30},
            )[0],
        }

        salas = {
            "101": Sala.objects.get_or_create(
                nome="sala 101",
                defaults={
                    "tipo_sala": Sala.TipoSala.COMUM,
                    "capacidade_alunos": 40,
                    "localizacao": "bloco a",
                },
            )[0],
            "lab": Sala.objects.get_or_create(
                nome="laboratorio 01",
                defaults={
                    "tipo_sala": Sala.TipoSala.LABORATORIO,
                    "capacidade_alunos": 35,
                    "localizacao": "bloco b",
                },
            )[0],
        }
        salas["101"].recursos.add(projetor)
        salas["lab"].recursos.add(projetor, laboratorio)

        horarios = {
            "seg_19": Horario.objects.get_or_create(
                dia_semana=Horario.DiaSemana.SEGUNDA,
                horario_inicio=time(19, 0),
                horario_fim=time(21, 0),
            )[0],
            "ter_19": Horario.objects.get_or_create(
                dia_semana=Horario.DiaSemana.TERCA,
                horario_inicio=time(19, 0),
                horario_fim=time(21, 0),
            )[0],
            "qua_19": Horario.objects.get_or_create(
                dia_semana=Horario.DiaSemana.QUARTA,
                horario_inicio=time(19, 0),
                horario_fim=time(21, 0),
            )[0],
        }

        return {
            "periodo": periodo,
            "professores": professores,
            "disciplinas": disciplinas,
            "turmas": turmas,
            "salas": salas,
            "horarios": horarios,
        }

    def _criar_disponibilidades(self, dados):
        """cria bloqueios de disponibilidade para simular dado real."""

        DisponibilidadeProfessor.objects.get_or_create(
            professor=dados["professores"]["ana"],
            horario=dados["horarios"]["qua_19"],
            defaults={
                "disponivel": False,
                "observacao": "reuniao fixa do colegiado",
            },
        )

    def _criar_alocacoes(self, dados):
        """cria alocacoes de exemplo sem duplicar a grade."""

        cenarios = [
            {
                "periodo_letivo": dados["periodo"],
                "professor": dados["professores"]["ana"],
                "disciplina": dados["disciplinas"]["bd"],
                "turma": dados["turmas"]["si1"],
                "sala": dados["salas"]["101"],
                "horario": dados["horarios"]["seg_19"],
                "status": Alocacao.Status.CONFIRMADA,
            },
            {
                "periodo_letivo": dados["periodo"],
                "professor": dados["professores"]["carla"],
                "disciplina": dados["disciplinas"]["lp"],
                "turma": dados["turmas"]["si2"],
                "sala": dados["salas"]["lab"],
                "horario": dados["horarios"]["ter_19"],
                "status": Alocacao.Status.PLANEJADA,
            },
        ]

        total = 0
        for cenario in cenarios:
            existe = Alocacao.objects.filter(
                periodo_letivo=cenario["periodo_letivo"],
                turma=cenario["turma"],
                disciplina=cenario["disciplina"],
                professor=cenario["professor"],
            ).exists()
            if existe:
                continue

            criar_alocacao(**cenario)
            total += 1

        return Alocacao.objects.filter(periodo_letivo=dados["periodo"]).count()
