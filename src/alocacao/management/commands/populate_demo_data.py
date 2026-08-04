from datetime import date, time

from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.db.models import Q

from academico.models import Curso, Disciplina, PeriodoLetivo
from alocacao.models import Alocacao, Horario
from infraestrutura.models import Sala
from pessoas.models import Professor, Turma


class Command(BaseCommand):
    help = "Popula o banco com dados de exemplo para testes e demonstração do dashboard"

    def handle(self, *args, **options):
        periodo, _ = PeriodoLetivo.objects.get_or_create(
            ano=2026,
            semestre=2,
            defaults={
                "data_inicio": date(2026, 8, 1),
                "data_fim": date(2026, 12, 15),
                "ativo": True,
            },
        )

        cursos_data = [
            ("Sistemas de Informação", "SI"),
            ("Administração", "ADM"),
            ("Engenharia de Software", "ENG"),
        ]
        cursos = []
        for nome, codigo in cursos_data:
            curso = Curso.objects.filter(Q(codigo=codigo) | Q(nome=nome)).first()
            if not curso:
                curso = Curso.objects.create(codigo=codigo, nome=nome, ativo=True)
            else:
                updates = {}
                if curso.codigo != codigo:
                    updates["codigo"] = codigo
                if curso.nome != nome:
                    updates["nome"] = nome
                if updates:
                    Curso.objects.filter(pk=curso.pk).update(**updates)
            cursos.append(curso)

        disciplinas_data = [
            (cursos[0], "Algoritmos e Lógica de Programação", "ALG001", 4),
            (cursos[0], "Banco de Dados", "BD001", 4),
            (cursos[0], "Engenharia de Requisitos", "ER001", 3),
            (cursos[1], "Gestão Estratégica", "GE001", 3),
            (cursos[1], "Contabilidade Gerencial", "CG001", 3),
            (cursos[2], "Arquitetura de Software", "AS001", 4),
            (cursos[2], "Testes de Software", "TS001", 3),
        ]
        disciplinas = []
        for curso, nome, codigo, carga in disciplinas_data:
            disciplina = Disciplina.objects.filter(Q(curso=curso, codigo=codigo) | Q(curso=curso, nome=nome)).first()
            if not disciplina:
                disciplina = Disciplina.objects.create(
                    curso=curso,
                    codigo=codigo,
                    nome=nome,
                    carga_horaria_semanal=carga,
                    periodo_recomendado=2,
                    ativo=True,
                )
            disciplinas.append(disciplina)

        professores_data = [
            ("Ana Paula Santos", "ana.santos@faculdade.edu", "Banco de Dados", 16, True),
            ("Bruno Mendes", "bruno.mendes@faculdade.edu", "Redes", 12, True),
            ("Carla Nogueira", "carla.nogueira@faculdade.edu", "Engenharia de Software", 14, True),
            ("Diego Fonseca", "diego.fonseca@faculdade.edu", "Gestão", 10, True),
            ("Elisa Costa", "elisa.costa@faculdade.edu", "Matemática", 12, True),
            ("Fernando Lima", "fernando.lima@faculdade.edu", "Segurança", 8, True),
            ("Gabriela Torres", "gabriela.torres@faculdade.edu", "Arquitetura", 14, True),
            ("Henrique Rocha", "henrique.rocha@faculdade.edu", "DevOps", 10, False),
        ]
        professores = []
        for nome, email, especialidade, carga, ativo in professores_data:
            professor, _ = Professor.objects.get_or_create(
                email=email,
                defaults={
                    "nome": nome,
                    "especialidade": especialidade,
                    "carga_horaria_maxima": carga,
                    "ativo": ativo,
                },
            )
            professores.append(professor)

        salas_data = [
            ("Sala 101", "comum", 40, "Bloco A"),
            ("Sala 102", "comum", 35, "Bloco A"),
            ("Laboratório 01", "laboratorio", 25, "Bloco B"),
            ("Sala 203", "comum", 50, "Bloco B"),
            ("Auditório Central", "auditorio", 80, "Bloco C"),
            ("Sala 305", "comum", 30, "Bloco C"),
            ("Sala 306", "comum", 28, "Bloco C"),
            ("Sala 410", "comum", 20, "Bloco D"),
        ]
        salas = []
        for nome, tipo, capacidade, localizacao in salas_data:
            sala, _ = Sala.objects.get_or_create(
                nome=nome,
                defaults={
                    "tipo_sala": tipo,
                    "capacidade_alunos": capacidade,
                    "localizacao": localizacao,
                    "ativo": True,
                },
            )
            if nome == "Sala 410":
                sala.ativo = False
                sala.save(update_fields=["ativo"])
            salas.append(sala)

        turmas_data = [
            (cursos[0], "SI-2026-01", "matutino", 35),
            (cursos[0], "SI-2026-02", "vespertino", 30),
            (cursos[1], "ADM-2026-01", "noturno", 28),
            (cursos[1], "ADM-2026-02", "integral", 24),
            (cursos[2], "ENG-2026-01", "matutino", 32),
            (cursos[2], "ENG-2026-02", "vespertino", 26),
        ]
        turmas = []
        for curso, nome, turno, alunos in turmas_data:
            turma, _ = Turma.objects.get_or_create(
                curso=curso,
                periodo_letivo=periodo,
                nome=nome,
                defaults={"turno": turno, "numero_alunos": alunos, "ativo": True},
            )
            turmas.append(turma)

        horarios_data = [
            ("1", time(8, 0), time(10, 0)),
            ("1", time(10, 0), time(12, 0)),
            ("2", time(8, 0), time(10, 0)),
            ("2", time(14, 0), time(16, 0)),
            ("3", time(8, 0), time(10, 0)),
            ("4", time(10, 0), time(12, 0)),
            ("5", time(8, 0), time(10, 0)),
            ("5", time(14, 0), time(16, 0)),
        ]
        horarios = []
        for dia, inicio, fim in horarios_data:
            horario, _ = Horario.objects.get_or_create(
                dia_semana=dia,
                horario_inicio=inicio,
                horario_fim=fim,
            )
            horarios.append(horario)

        allocations_data = [
            (periodo, professores[0], disciplinas[0], turmas[0], salas[0], horarios[0], "confirmada"),
            (periodo, professores[1], disciplinas[1], turmas[0], salas[1], horarios[1], "confirmada"),
            (periodo, professores[2], disciplinas[2], turmas[1], salas[2], horarios[2], "planejada"),
            (periodo, professores[3], disciplinas[3], turmas[2], salas[3], horarios[3], "confirmada"),
            (periodo, professores[4], disciplinas[4], turmas[3], salas[4], horarios[4], "planejada"),
            (periodo, professores[5], disciplinas[5], turmas[4], salas[5], horarios[5], "confirmada"),
            (periodo, professores[0], disciplinas[6], turmas[5], salas[6], horarios[6], "planejada"),
            (periodo, professores[2], disciplinas[0], turmas[1], salas[1], horarios[7], "confirmada"),
            (periodo, professores[6], disciplinas[3], turmas[2], salas[2], horarios[0], "planejada"),
            (periodo, professores[6], disciplinas[5], turmas[4], salas[3], horarios[2], "confirmada"),
        ]

        for periodo_obj, professor, disciplina, turma, sala, horario, status in allocations_data:
            try:
                Alocacao.objects.get_or_create(
                    periodo_letivo=periodo_obj,
                    professor=professor,
                    disciplina=disciplina,
                    turma=turma,
                    sala=sala,
                    horario=horario,
                    status=status,
                )
            except IntegrityError:
                continue

        # create a conflict by reusing the same professor and time on a second allocation
        try:
            Alocacao.objects.get_or_create(
                periodo_letivo=periodo,
                professor=professores[0],
                disciplina=disciplinas[6],
                turma=turmas[5],
                sala=salas[7],
                horario=horarios[0],
                status="confirmada",
            )
        except IntegrityError:
            pass

        self.stdout.write(
            self.style.SUCCESS(
                f"Dados de demonstração criados: {Professor.objects.count()} professores, {Curso.objects.count()} cursos, {Disciplina.objects.count()} disciplinas, {Turma.objects.count()} turmas, {Sala.objects.count()} salas e {Alocacao.objects.count()} alocações."
            )
        )
