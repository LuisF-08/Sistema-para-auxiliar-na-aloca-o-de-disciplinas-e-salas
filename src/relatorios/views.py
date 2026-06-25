import csv
import io
from datetime import datetime

from django.db.models import Count, Sum, F, FloatField, ExpressionWrapper, Q
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from alocacao.models import Alocacao, Horario
from academico.models import PeriodoLetivo
from infraestrutura.models import Sala
from pessoas.models import Professor, Turma


STATUS_ATIVOS = ["planejada", "confirmada"]

DIAS_SEMANA = {
    1: "Segunda-feira",
    2: "Terça-feira",
    3: "Quarta-feira",
    4: "Quinta-feira",
    5: "Sexta-feira",
    6: "Sábado",
}

DIAS_SEMANA_ABREV = {
    1: "Seg",
    2: "Ter",
    3: "Qua",
    4: "Qui",
    5: "Sex",
    6: "Sáb",
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
    def get(self, request):
        periodo = _periodo_ativo()
        turma_id = request.GET.get("turma")
        professor_id = request.GET.get("professor")

        turmas = Turma.objects.filter(ativo=True).select_related("curso", "periodo_letivo").order_by("nome")
        professores = Professor.objects.filter(ativo=True).order_by("nome")

        turma_selecionada = None
        professor_selecionado = None

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
        else:
            qs = qs.none()

        alocacoes = list(
            qs.select_related("horario", "disciplina", "professor", "turma", "sala")
            .order_by("horario__dia_semana", "horario__horario_inicio")
        )
        for a in alocacoes:
            a.dia_nome = DIAS_SEMANA.get(a.horario.dia_semana, "")

        ctx = {
            "periodo": periodo,
            "turmas": turmas,
            "professores": professores,
            "turma_selecionada": turma_selecionada,
            "professor_selecionado": professor_selecionado,
            "alocacoes": alocacoes,
        }
        return render(request, "relatorios/grade.html", ctx)


def exportar_csv(request):
    nome_arquivo = f"grade_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    response["Content-Disposition"] = f'attachment; filename="{nome_arquivo}"'

    writer = csv.writer(response, delimiter=";")
    writer.writerow([
        "Dia da Semana", "Horário Início", "Horário Fim",
        "Disciplina", "Professor", "Turma",
        "Sala", "Capacidade Sala", "N. Alunos", "Assentos Ociosos", "Status",
    ])

    alocacoes = (
        Alocacao.objects
        .filter(status__in=STATUS_ATIVOS)
        .select_related("horario", "disciplina", "professor", "turma", "sala")
        .order_by("horario__dia_semana", "horario__horario_inicio")
    )

    for a in alocacoes:
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

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=2.0 * cm,
        bottomMargin=2.0 * cm,
        title="Grade Horária — SisAloc",
    )

    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle(
        "titulo",
        parent=estilos["Heading1"],
        fontSize=18,
        textColor=colors.HexColor("#1e3a5f"),
        alignment=TA_CENTER,
        spaceAfter=4,
    )

    elementos = [
        Paragraph("Grade Horária Completa", estilo_titulo),
        Paragraph(
            f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
            estilos["Normal"],
        ),
        Spacer(1, 0.4 * cm),
    ]

    cabecalho = ["Dia", "Início", "Fim", "Disciplina", "Professor", "Turma", "Sala", "Alunos"]
    alocacoes = (
        Alocacao.objects
        .filter(status__in=STATUS_ATIVOS)
        .select_related("horario", "disciplina", "professor", "turma", "sala")
        .order_by("horario__dia_semana", "horario__horario_inicio")
    )

    dados = [cabecalho]
    for a in alocacoes:
        dados.append([
            DIAS_SEMANA_ABREV.get(a.horario.dia_semana, ""),
            a.horario.horario_inicio.strftime("%H:%M"),
            a.horario.horario_fim.strftime("%H:%M"),
            a.disciplina.nome,
            a.professor.nome,
            a.turma.nome,
            a.sala.nome,
            str(a.turma.numero_alunos),
        ])

    if len(dados) == 1:
        dados.append(["Sem alocações ativas", "", "", "", "", "", "", ""])

    col_widths = [1.8*cm, 1.8*cm, 1.8*cm, 5.5*cm, 5.0*cm, 3.5*cm, 3.5*cm, 2.0*cm]
    tabela = Table(dados, colWidths=col_widths, repeatRows=1)
    tabela.setStyle(TableStyle([
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
    ]))
    elementos.append(tabela)

    try:
        doc.build(elementos)
    except Exception as exc:
        import logging
        logging.getLogger(__name__).error("Erro ao gerar PDF: %s", exc, exc_info=True)
        return HttpResponse(f"Erro ao gerar PDF: {exc}", status=500)

    buffer.seek(0)
    nome = f"grade_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{nome}"'
    return response
