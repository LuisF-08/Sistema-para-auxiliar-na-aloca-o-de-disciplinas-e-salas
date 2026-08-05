import csv
import io
from datetime import datetime

from collections import defaultdict

from django.db.models import Count, Sum, F, FloatField, ExpressionWrapper, Q
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from alocacao.models import Alocacao, Horario
from academico.models import Curso, PeriodoLetivo
from infraestrutura.models import Sala
from pessoas.models import Professor, Turma


STATUS_ATIVOS = ["planejada", "confirmada"]

DIAS_SEMANA = {
    "1": "Segunda-feira",
    "2": "Terça-feira",
    "3": "Quarta-feira",
    "4": "Quinta-feira",
    "5": "Sexta-feira",
    "6": "Sábado",
}

DIAS_SEMANA_ABREV = {
    "1": "Seg",
    "2": "Ter",
    "3": "Qua",
    "4": "Qui",
    "5": "Sex",
    "6": "Sáb",
}


def _periodo_ativo():
    return PeriodoLetivo.objects.filter(ativo=True).first()


def calcular_taxa_ocupacao(periodo=None):
    total_salas = Sala.objects.filter(ativo=True).count()
    if total_salas == 0:
        return {"taxa": 0.0, "salas_ocupadas": 0, "total_salas": 0}

    qs = Alocacao.objects.filter(status__in=STATUS_ATIVOS)
    if periodo:
        qs = qs.filter(periodo_letivo=periodo)

    salas_ocupadas = qs.values("sala_id").distinct().count()
    taxa = round((salas_ocupadas / total_salas) * 100, 1)
    return {"taxa": taxa, "salas_ocupadas": salas_ocupadas, "total_salas": total_salas}


def calcular_eficiencia_espaco(periodo=None):
    qs = Alocacao.objects.filter(status__in=STATUS_ATIVOS)
    if periodo:
        qs = qs.filter(periodo_letivo=periodo)

    alocacoes = list(
        qs.annotate(
            assentos_ociosos=ExpressionWrapper(
                F("sala__capacidade_alunos") - F("turma__numero_alunos"),
                output_field=FloatField(),
            )
        )
        .filter(assentos_ociosos__gte=0)
        .values(
            "sala__nome",
            "sala__capacidade_alunos",
            "turma__nome",
            "turma__numero_alunos",
            "assentos_ociosos",
        )
    )

    if not alocacoes:
        return {"media_assentos_ociosos": 0.0, "detalhe_por_sala": []}

    media = round(sum(item["assentos_ociosos"] for item in alocacoes) / len(alocacoes), 1)
    return {"media_assentos_ociosos": media, "detalhe_por_sala": alocacoes}


def calcular_horarios_pico(periodo=None, top_n=5):
    filtro = Q(alocacoes__status__in=STATUS_ATIVOS)
    if periodo:
        filtro &= Q(alocacoes__periodo_letivo=periodo)

    pico = list(
        Horario.objects
        .annotate(total_alocacoes=Count("alocacoes", filter=filtro))
        .filter(total_alocacoes__gt=0)
        .order_by("-total_alocacoes")
        .values("dia_semana", "horario_inicio", "horario_fim", "total_alocacoes")[:top_n]
    )
    for item in pico:
        item["dia_nome"] = DIAS_SEMANA.get(item["dia_semana"], "")
    return pico


def detectar_conflitos_ativos(periodo=None):
    qs = Alocacao.objects.filter(status__in=STATUS_ATIVOS)
    if periodo:
        qs = qs.filter(periodo_letivo=periodo)

    # RC1: mesma sala no mesmo horario
    grupos_sala = (
        qs.values("sala_id", "horario_id")
        .annotate(total=Count("id"))
        .filter(total__gt=1)
    )
    conflitos_sala = []
    for grupo in grupos_sala:
        alocacoes = qs.filter(
            sala_id=grupo["sala_id"], horario_id=grupo["horario_id"]
        ).select_related("sala", "horario", "professor", "disciplina", "turma")
        first = alocacoes.first()
        conflitos_sala.append({
            "tipo": "Sala Duplicada",
            "sala": first.sala.nome,
            "horario": str(first.horario),
            "envolvidos": [
                f"{a.professor.nome} — {a.disciplina.nome}" for a in alocacoes
            ],
        })

    # RC2: mesmo professor no mesmo horario
    grupos_professor = (
        qs.values("professor_id", "horario_id")
        .annotate(total=Count("id"))
        .filter(total__gt=1)
    )
    conflitos_professor = []
    for grupo in grupos_professor:
        alocacoes = qs.filter(
            professor_id=grupo["professor_id"], horario_id=grupo["horario_id"]
        ).select_related("sala", "horario", "professor", "disciplina")
        first = alocacoes.first()
        conflitos_professor.append({
            "tipo": "Professor Duplicado",
            "professor": first.professor.nome,
            "horario": str(first.horario),
            "envolvidos": [
                f"{a.sala.nome} — {a.disciplina.nome}" for a in alocacoes
            ],
        })

    return {
        "total": len(conflitos_sala) + len(conflitos_professor),
        "por_sala": conflitos_sala,
        "por_professor": conflitos_professor,
    }


class DashboardView(View):
    def get(self, request):
        periodo = _periodo_ativo()

        taxa = calcular_taxa_ocupacao(periodo)
        eficiencia = calcular_eficiencia_espaco(periodo)
        conflitos = detectar_conflitos_ativos(periodo)
        horarios_pico = calcular_horarios_pico(periodo)

        qs_total = Alocacao.objects.filter(status__in=STATUS_ATIVOS)
        if periodo:
            qs_total = qs_total.filter(periodo_letivo=periodo)

        ctx = {
            "periodo": periodo,
            "total_alocacoes": qs_total.count(),
            "total_salas": taxa["total_salas"],
            "salas_ocupadas": taxa["salas_ocupadas"],   
            "taxa_ocupacao": taxa["taxa"],
            "media_ociosos": eficiencia["media_assentos_ociosos"],
            "total_conflitos": conflitos["total"],
            "conflitos_sala": conflitos["por_sala"],
            "conflitos_professor": conflitos["por_professor"],
            "horarios_pico": horarios_pico,
        }
        return render(request, "relatorios/dashboard.html", ctx)


class RelatorioProfessoresView(View):
    def get(self, request):
        periodo = _periodo_ativo()
        professores = Professor.objects.filter(ativo=True).order_by("nome")

        dados = []
        for prof in professores:
            qs = Alocacao.objects.filter(professor=prof, status__in=STATUS_ATIVOS)
            if periodo:
                qs = qs.filter(periodo_letivo=periodo)

            carga = qs.aggregate(total=Sum("disciplina__carga_horaria_semanal"))["total"] or 0
            num_alocacoes = qs.count()
            percentual = round((carga / prof.carga_horaria_maxima) * 100, 1) if prof.carga_horaria_maxima else 0

            dados.append({
                "professor": prof,
                "carga_alocada": carga,
                "carga_maxima": prof.carga_horaria_maxima,
                "num_alocacoes": num_alocacoes,
                "percentual": percentual,
                "no_limite": percentual >= 80,
            })

        ctx = {"periodo": periodo, "dados": dados}
        return render(request, "relatorios/professores.html", ctx)


class RelatorioSalasView(View):
    def get(self, request):
        periodo = _periodo_ativo()
        salas = Sala.objects.filter(ativo=True).order_by("nome")

        dados = []
        for sala in salas:
            qs = Alocacao.objects.filter(sala=sala, status__in=STATUS_ATIVOS)
            if periodo:
                qs = qs.filter(periodo_letivo=periodo)

            num_alocacoes = qs.count()
            dados.append({
                "sala": sala,
                "num_alocacoes": num_alocacoes,
                "em_uso": num_alocacoes > 0,
            })

        ctx = {"periodo": periodo, "dados": dados}
        return render(request, "relatorios/salas.html", ctx)


class RelatorioGradeView(View):
    DIAS = ["1", "2", "3", "4", "5", "6"]

    def get(self, request):
        periodo = _periodo_ativo()
        turma_id = request.GET.get("turma")
        professor_id = request.GET.get("professor")
        curso_id = request.GET.get("curso", "todos")

        turmas = Turma.objects.filter(ativo=True).select_related("curso", "periodo_letivo").order_by("nome")
        professores = Professor.objects.filter(ativo=True).order_by("nome")
        cursos = Curso.objects.all().order_by("nome")

        turma_selecionada = None
        professor_selecionado = None
        curso_selecionado = None

        tem_filtro = bool(turma_id or professor_id or (curso_id and curso_id != "todos"))

        qs = Alocacao.objects.filter(status__in=STATUS_ATIVOS)
        if periodo:
            qs = qs.filter(periodo_letivo=periodo)

        if turma_id:
            try:
                turma_selecionada = Turma.objects.get(pk=turma_id)
                qs = qs.filter(turma=turma_selecionada)
            except Turma.DoesNotExist:
                qs = qs.none()
        elif professor_id:
            try:
                professor_selecionado = Professor.objects.get(pk=professor_id)
                qs = qs.filter(professor=professor_selecionado)
            except Professor.DoesNotExist:
                qs = qs.none()
        elif curso_id and curso_id != "todos":
            try:
                curso_selecionado = Curso.objects.get(pk=curso_id)
                qs = qs.filter(disciplina__curso=curso_selecionado)
            except Curso.DoesNotExist:
                qs = qs.none()

        if not tem_filtro:
            linhas_grade = []
        else:
            alocacoes = list(
                qs.select_related("horario", "disciplina", "professor", "turma", "sala")
            )
            linhas_grade = _build_grade_matrix(alocacoes, self.DIAS)

        dias_info = [
            {"num": d, "nome": DIAS_SEMANA[d], "abrev": DIAS_SEMANA_ABREV[d]}
            for d in self.DIAS
        ]

        ctx = {
            "periodo": periodo,
            "turmas": turmas,
            "professores": professores,
            "cursos": cursos,
            "turma_selecionada": turma_selecionada,
            "professor_selecionado": professor_selecionado,
            "curso_selecionado": curso_selecionado,
            "curso_id": curso_id,
            "dias_info": dias_info,
            "linhas_grade": linhas_grade,
            "tem_filtro": tem_filtro,
        }
        return render(request, "relatorios/grade.html", ctx)


def _qs_grade_filtrada(request):
    periodo = _periodo_ativo()
    qs = (
        Alocacao.objects
        .filter(status__in=STATUS_ATIVOS, horario__isnull=False)
        .select_related("horario", "disciplina", "professor", "turma", "sala")
        .order_by("horario__dia_semana", "horario__horario_inicio")
    )
    if periodo:
        qs = qs.filter(periodo_letivo=periodo)
    turma_id = request.GET.get("turma")
    professor_id = request.GET.get("professor")
    curso_id = request.GET.get("curso")
    if turma_id:
        qs = qs.filter(turma_id=turma_id)
    elif professor_id:
        qs = qs.filter(professor_id=professor_id)
    elif curso_id and curso_id != "todos":
        qs = qs.filter(disciplina__curso_id=curso_id)
    return qs


def _build_grade_matrix(alocacoes, dias):
    """Monta a estrutura {slot_hora: {dia_str: [alocacoes]}} para a grade visual."""
    matriz = defaultdict(lambda: defaultdict(list))
    for a in alocacoes:
        if a.horario:
            slot = a.horario.horario_inicio.strftime("%H:%M")
            matriz[slot][a.horario.dia_semana].append(a)
    slots = sorted(matriz.keys())
    linhas = [
        {"hora": slot, "celulas": [{"dia": d, "alocacoes": matriz[slot][d]} for d in dias]}
        for slot in slots
    ]
    return linhas


def _qs_professores():
    periodo = _periodo_ativo()
    professores = Professor.objects.filter(ativo=True).order_by("nome")
    dados = []
    for prof in professores:
        qs = Alocacao.objects.filter(professor=prof, status__in=STATUS_ATIVOS)
        if periodo:
            qs = qs.filter(periodo_letivo=periodo)
        carga = qs.aggregate(total=Sum("disciplina__carga_horaria_semanal"))["total"] or 0
        num_alocacoes = qs.count()
        percentual = round((carga / prof.carga_horaria_maxima) * 100, 1) if prof.carga_horaria_maxima else 0
        dados.append({
            "nome": prof.nome,
            "especialidade": prof.especialidade or "",
            "num_alocacoes": num_alocacoes,
            "carga_alocada": carga,
            "carga_maxima": prof.carga_horaria_maxima or 0,
            "percentual": percentual,
        })
    return dados


def _qs_salas():
    periodo = _periodo_ativo()
    salas = Sala.objects.filter(ativo=True).order_by("nome")
    dados = []
    for sala in salas:
        qs = Alocacao.objects.filter(sala=sala, status__in=STATUS_ATIVOS)
        if periodo:
            qs = qs.filter(periodo_letivo=periodo)
        num_alocacoes = qs.count()
        dados.append({
            "nome": sala.nome,
            "tipo_sala": sala.tipo_sala,
            "capacidade_alunos": sala.capacidade_alunos,
            "localizacao": sala.localizacao or "",
            "num_alocacoes": num_alocacoes,
            "em_uso": num_alocacoes > 0,
        })
    return dados


def exportar_csv(request):
    tipo = request.GET.get("tipo", "grade")
    agora = datetime.now().strftime("%Y%m%d_%H%M")

    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")

    writer = csv.writer(response, delimiter=";")

    if tipo == "professores":
        response["Content-Disposition"] = f'attachment; filename="professores_{agora}.csv"'
        writer.writerow(["Professor", "Especialidade", "Alocações", "Carga Alocada (h)", "Carga Máxima (h)", "Utilização (%)"])
        for d in _qs_professores():
            writer.writerow([d["nome"], d["especialidade"], d["num_alocacoes"],
                             d["carga_alocada"], d["carga_maxima"], d["percentual"]])

    elif tipo == "salas":
        response["Content-Disposition"] = f'attachment; filename="salas_{agora}.csv"'
        writer.writerow(["Sala", "Tipo", "Capacidade", "Localização", "Alocações", "Status"])
        for d in _qs_salas():
            writer.writerow([d["nome"], d["tipo_sala"], d["capacidade_alunos"],
                             d["localizacao"], d["num_alocacoes"],
                             "Em uso" if d["em_uso"] else "Ociosa"])

    else:
        response["Content-Disposition"] = f'attachment; filename="grade_{agora}.csv"'
        writer.writerow([
            "Dia da Semana", "Horário Início", "Horário Fim",
            "Disciplina", "Professor", "Turma",
            "Sala", "Capacidade Sala", "N. Alunos", "Assentos Ociosos", "Status",
        ])
        for a in _qs_grade_filtrada(request):
            ociosos = max(a.sala.capacidade_alunos - a.turma.numero_alunos, 0)
            writer.writerow([
                DIAS_SEMANA.get(a.horario.dia_semana, a.horario.dia_semana),
                a.horario.horario_inicio.strftime("%H:%M"),
                a.horario.horario_fim.strftime("%H:%M"),
                a.disciplina.nome,
                a.professor.nome,
                a.turma.nome,
                a.sala.nome,
                a.sala.capacidade_alunos,
                a.turma.numero_alunos,
                ociosos,
                a.status,
            ])

    return response


def _pdf_estilo_tabela(colors, TableStyle):
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4f8")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c8d6e5")),
        ("BOX", (0, 0), (-1, -1), 1.0, colors.HexColor("#1e3a5f")),
    ])


def exportar_pdf(request):
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib.enums import TA_CENTER
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    except ImportError:
        return HttpResponse(
            "ReportLab não instalado. Execute: pip install reportlab",
            status=500,
        )

    tipo = request.GET.get("tipo", "grade")
    agora = datetime.now()
    agora_str = agora.strftime("%Y%m%d_%H%M")
    agora_fmt = agora.strftime("%d/%m/%Y às %H:%M")

    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle(
        "titulo",
        parent=estilos["Heading1"],
        fontSize=16,
        textColor=colors.HexColor("#1e3a5f"),
        alignment=TA_CENTER,
        spaceAfter=4,
    )

    buffer = io.BytesIO()

    if tipo == "professores":
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                rightMargin=1.5*cm, leftMargin=1.5*cm,
                                topMargin=2.0*cm, bottomMargin=2.0*cm,
                                title="Carga Horária dos Professores — SisAloc")
        cabecalho = ["Professor", "Especialidade", "Alocações", "Carga Aloc. (h)", "Carga Máx. (h)", "Utiliz. (%)"]
        linhas = [cabecalho]
        for d in _qs_professores():
            linhas.append([d["nome"], d["especialidade"], str(d["num_alocacoes"]),
                           str(d["carga_alocada"]), str(d["carga_maxima"]), f"{d['percentual']}%"])
        if len(linhas) == 1:
            linhas.append(["Nenhum professor ativo", "", "", "", "", ""])
        col_widths = [5.5*cm, 4.0*cm, 2.5*cm, 3.0*cm, 3.0*cm, 2.5*cm]
        nome_arquivo = f"professores_{agora_str}.pdf"
        titulo_doc = "Carga Horária dos Professores"

    elif tipo == "salas":
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                rightMargin=1.5*cm, leftMargin=1.5*cm,
                                topMargin=2.0*cm, bottomMargin=2.0*cm,
                                title="Ocupação de Salas — SisAloc")
        cabecalho = ["Sala", "Tipo", "Capacidade", "Localização", "Alocações", "Status"]
        linhas = [cabecalho]
        for d in _qs_salas():
            linhas.append([d["nome"], d["tipo_sala"], str(d["capacidade_alunos"]),
                           d["localizacao"], str(d["num_alocacoes"]),
                           "Em uso" if d["em_uso"] else "Ociosa"])
        if len(linhas) == 1:
            linhas.append(["Nenhuma sala ativa", "", "", "", "", ""])
        col_widths = [4.5*cm, 3.0*cm, 2.5*cm, 4.0*cm, 2.5*cm, 2.5*cm]
        nome_arquivo = f"salas_{agora_str}.pdf"
        titulo_doc = "Ocupação de Salas"

    else:
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4),
                                rightMargin=1.5*cm, leftMargin=1.5*cm,
                                topMargin=2.0*cm, bottomMargin=2.0*cm,
                                title="Grade Horária — SisAloc")
        cabecalho = ["Dia", "Início", "Fim", "Disciplina", "Professor", "Turma", "Sala", "Alunos"]
        linhas = [cabecalho]
        for a in _qs_grade_filtrada(request):
            linhas.append([
                DIAS_SEMANA_ABREV.get(a.horario.dia_semana, ""),
                a.horario.horario_inicio.strftime("%H:%M"),
                a.horario.horario_fim.strftime("%H:%M"),
                a.disciplina.nome,
                a.professor.nome,
                a.turma.nome,
                a.sala.nome,
                str(a.turma.numero_alunos),
            ])
        if len(linhas) == 1:
            linhas.append(["Sem alocações ativas", "", "", "", "", "", "", ""])
        col_widths = [1.8*cm, 1.8*cm, 1.8*cm, 5.5*cm, 5.0*cm, 3.5*cm, 3.5*cm, 2.0*cm]
        nome_arquivo = f"grade_{agora_str}.pdf"
        titulo_doc = "Grade Horária"

    tabela = Table(linhas, colWidths=col_widths, repeatRows=1)
    tabela.setStyle(_pdf_estilo_tabela(colors, TableStyle))

    elementos = [
        Paragraph(titulo_doc, estilo_titulo),
        Paragraph(f"Gerado em {agora_fmt}", estilos["Normal"]),
        Spacer(1, 0.4 * cm),
        tabela,
    ]

    try:
        doc.build(elementos)
    except Exception as exc:
        import logging
        logging.getLogger(__name__).error("Erro ao gerar PDF: %s", exc, exc_info=True)
        return HttpResponse(f"Erro ao gerar PDF: {exc}", status=500)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{nome_arquivo}"'
    return response