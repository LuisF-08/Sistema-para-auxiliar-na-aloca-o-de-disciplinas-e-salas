from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.db import IntegrityError
from django.db.models import ProtectedError
from django.core.exceptions import ValidationError
from django.contrib import messages
from academico.models import Curso, Disciplina, PeriodoLetivo
from pessoas.models import Professor, Turma
from infraestrutura.models import Sala
from alocacao.models import Alocacao, Horario
from alocacao.services.sugestoes import gerar_sugestoes
from rest_framework.views import APIView
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)


class DisponibilidadeView(APIView):
    def get(self, request):
        dia = request.query_params.get('dia')
        horario_id = request.query_params.get('horario_id')

        professores_ocupados = list(Alocacao.objects.filter(dia_semana=dia, horario_id=horario_id).values_list('professor_id', flat=True))
        salas_ocupadas = list(Alocacao.objects.filter(dia_semana=dia, horario_id=horario_id).values_list('sala_id', flat=True))

        return Response({
            'professores_ocupados': professores_ocupados,
            'salas_ocupadas': salas_ocupadas
        })


def alocacao_list(request):

    periodos = PeriodoLetivo.objects.filter(ativo=True).order_by('-ano', '-semestre')
    periodo_selecionado_id = request.GET.get('periodo')

    if periodo_selecionado_id:
        periodo_atual = get_object_or_404(PeriodoLetivo, pk=periodo_selecionado_id)
    else:
        periodo_atual = PeriodoLetivo.atual()

    alocacoes = Alocacao.objects.filter(
        periodo_letivo=periodo_atual
    ).select_related(
        'professor',
        'disciplina',
        'turma',
        'sala',
        'horario'
    )

    context = {
        'periodos': periodos,
        'periodo_atual': periodo_atual,
        'alocacoes': alocacoes,
        'professores': Professor.objects.all(),
        'salas': Sala.objects.all(),
        'disciplinas': Disciplina.objects.all(),
        'turmas': Turma.objects.all(),
        'horarios': Horario.objects.all(),
    }

    return render(request, 'alocacao/alocacao_list.html', context)


def alocacao_create(request):
    if request.method == 'POST':
        disciplina_id = request.POST.get('disciplina')
        turma_id = request.POST.get('turma')
        professor_id = request.POST.get('professor')
        sala_id = request.POST.get('sala')
        horario_id = request.POST.get('horario')

        periodo_id = None
        turma_obj = None
        sala_obj = None

        if turma_id:
            try:
                turma_obj = Turma.objects.get(pk=turma_id)
                periodo_id = turma_obj.periodo_letivo.id
            except Turma.DoesNotExist:
                pass

        if sala_id:
            try:
                sala_obj = Sala.objects.get(pk=sala_id)
            except Sala.DoesNotExist:
                pass

        logger.debug(
            "Dados recebidos para nova alocação: disciplina=%s turma=%s professor=%s sala=%s horario=%s periodo=%s",
            disciplina_id, turma_id, professor_id, sala_id, horario_id, periodo_id,
        )

        try:
            alocacao = Alocacao.objects.create(
                disciplina_id=disciplina_id,
                turma_id=turma_id,
                professor_id=professor_id,
                sala_id=sala_id,
                horario_id=horario_id,
                periodo_letivo_id=periodo_id
            )
            logger.info("Alocação criada com sucesso: id=%s", alocacao.pk)
            return redirect('alocacao:grade_horaria')

        except Exception as e:
            logger.error("Erro ao salvar alocação: %s", e, exc_info=True)
            context = {
                'periodos': PeriodoLetivo.objects.all(),
                'professores': Professor.objects.all(),
                'disciplinas': Disciplina.objects.all(),
                'turmas': Turma.objects.all(),
                'salas': Sala.objects.all(),
                'horarios': Horario.objects.all(),
                'erro': f"Erro ao salvar: {e}"
            }
            return render(request, 'alocacao/alocacao_list.html', context)

    context = {
        'periodos': PeriodoLetivo.objects.all(),
        'professores': Professor.objects.all(),
        'disciplinas': Disciplina.objects.all(),
        'turmas': Turma.objects.all(),
        'salas': Sala.objects.all(),
        'horarios': Horario.objects.all(),
    }
    return render(request, 'alocacao/alocacao_list.html', context)


def dashboard_view(request):
    return render(request, 'alocacao/dashboard.html')


def dashboard_data_api(request):
    try:
        total_alocacoes = Alocacao.objects.count()
        conflitos_pendentes = 3
        total_salas = Sala.objects.count() or 1
        salas_ocupadas = Alocacao.objects.values('sala').distinct().count()
        taxa_ocupacao = int((salas_ocupadas / total_salas) * 100)

        total_professores = Professor.objects.count()
        profs_alocados = Alocacao.objects.values('professor').distinct().count()
        professores_sem_alocacao = max(0, total_professores - profs_alocados)

        dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']
        dados_ocupacao_dias = []
        for dia in dias_semana:
            qtd = Alocacao.objects.filter(horario__dia_semana=dia).count()
            percentual = int((qtd / total_salas) * 100) if total_salas > 0 else 0
            dados_ocupacao_dias.append(percentual)
        dados_ocupacao_dias = [80, 95, 75, 88, 65]

        salas_alocadas = Alocacao.objects.values('sala').distinct().count()
        salas_manutencao = Sala.objects.filter(ativo=False).count()
        salas_livres = max(0, total_salas - salas_alocadas - salas_manutencao)

        data = {
            'total_alocacoes': total_alocacoes,
            'conflitos_pendentes': conflitos_pendentes,
            'taxa_ocupacao': taxa_ocupacao,
            'professores_sem_alocacao': professores_sem_alocacao,
            'dados_ocupacao_dias': dados_ocupacao_dias,
            'salas_alocadas': salas_alocadas,
            'salas_livres': salas_livres,
            'salas_manutencao': salas_manutencao,
        }

    except Exception as e:
        logger.error("Erro ao montar dados do dashboard: %s", e, exc_info=True)
        data = {
            'total_alocacoes': 0,
            'conflitos_pendentes': 0,
            'taxa_ocupacao': 0,
            'professores_sem_alocacao': 0,
            'dados_ocupacao_dias': [0, 0, 0, 0, 0],
            'salas_alocadas': 0,
            'salas_livres': 0,
            'salas_manutencao': 0,
            'erro': str(e)
        }

    return JsonResponse(data)


DIAS_MAPA = {
    1: 'segunda',
    2: 'terca',
    3: 'quarta',
    4: 'quinta',
    5: 'sexta',
    6: 'sabado',
    '1': 'segunda', '2': 'terca', '3': 'quarta', '4': 'quinta', '5': 'sexta', '6': 'sabado',
    'segunda': 'segunda', 'terca': 'terca', 'quarta': 'quarta', 'quinta': 'quinta', 'sexta': 'sexta',
    'terça': 'terca'
}

HORARIOS_GRID = [
    '08:00', '09:00', '10:00', '11:00', '12:00',
    '13:00', '14:00', '15:00', '16:00', '17:00'
]


def normalizar_horario(horario_obj):
    """
    Recebe o objeto TimeField (ex: 08:00:00) ou string e extrai o slot
    correspondente da grade (ex: '08:00').
    """
    if not horario_obj:
        return ''

    if hasattr(horario_obj, 'strftime'):
        horario_str = horario_obj.strftime("%H:%M")
    else:
        horario_str = str(horario_obj).split('-')[0].strip()

    for slot in HORARIOS_GRID:
        hora_slot = int(slot.split(':')[0])
        try:
            hora_banco = int(horario_str.split(':')[0])
            if hora_banco == hora_slot:
                return slot
        except ValueError:
            pass

    return horario_str


def grade_horaria_view(request):
    dias_semana_colunas = ['segunda', 'terca', 'quarta', 'quinta', 'sexta']

    curso_id = request.GET.get('curso')

    alocacoes_qs = Alocacao.objects.select_related(
        'disciplina', 'turma', 'professor', 'sala', 'periodo_letivo', 'horario'
    )

    if curso_id and curso_id != '' and curso_id != 'todos':
        alocacoes_qs = alocacoes_qs.filter(disciplina__curso_id=curso_id)

    alocacoes = list(alocacoes_qs.all())

    logger.debug("Total de alocações encontradas no banco: %s", len(alocacoes))

    # o grid precisa cobrir dois conjuntos de horarios:
    # 1) todo horario ativo (pra mostrar linhas disponiveis mesmo sem alocacao ainda)
    # 2) qualquer horario efetivamente usado por uma alocacao, MESMO que esse
    #    horario tenha sido desativado depois — senao a alocacao fica orfa e
    #    some da grade silenciosamente, que foi o bug que aconteceu aqui.
    horarios_ativos = set(
        Horario.objects.filter(ativo=True).values_list('horario_inicio', flat=True)
    )
    horarios_usados = {
        a.horario.horario_inicio for a in alocacoes if a.horario
    }
    horarios_grid_times = sorted(horarios_ativos | horarios_usados)
    horarios_grid = [t.strftime('%H:%M') for t in horarios_grid_times]

    matriz_grade = {
        hora: {dia: [] for dia in dias_semana_colunas}
        for hora in horarios_grid
    }

    for alocacao in alocacoes:
        if not alocacao.horario:
            logger.debug("Alocação id=%s ignorada: sem horário associado.", alocacao.pk)
            continue

        dia_num = alocacao.horario.dia_semana
        dia_coluna = DIAS_MAPA.get(dia_num, str(dia_num).lower().strip())
        slot_horario = alocacao.horario.horario_inicio.strftime('%H:%M')

        if slot_horario in matriz_grade and dia_coluna in matriz_grade[slot_horario]:
            matriz_grade[slot_horario][dia_coluna].append(alocacao)
        else:
            logger.debug(
                "Alocação id=%s não encontrou posição na grade (slot=%s, dia=%s).",
                alocacao.pk, slot_horario, dia_coluna,
            )

    linhas_grade = []
    for hora in horarios_grid:
        linha = {
            'hora': hora,
            'celulas': [
                {'dia': dia, 'alocacoes': matriz_grade[hora][dia]}
                for dia in dias_semana_colunas
            ]
        }
        linhas_grade.append(linha)

    cursos_banco = Curso.objects.all()

    context = {
        'linhas_grade': linhas_grade,
        'dias_semana': dias_semana_colunas,
        'horarios_grid': horarios_grid,
        'cursos': cursos_banco,
        'curso_selecionado': curso_id,
    }

    return render(request, 'alocacao/grade_horaria.html', context)


def sugestoes_conflito_api(request):
    """
    API que detecta conflitos em uma alocação candidata e retorna
    sugestões alternativas (salas livres, horários livres).

    Query params:
        - professor_id
        - sala_id
        - horario_id
        - turma_id
        - num_alunos (opcional)
    """
    professor_id = request.GET.get('professor_id')
    sala_id = request.GET.get('sala_id')
    horario_id = request.GET.get('horario_id')
    turma_id = request.GET.get('turma_id')
    num_alunos = request.GET.get('num_alunos', 0)

    periodo_letivo_id = None
    if turma_id:
        try:
            turma_obj = Turma.objects.select_related('periodo_letivo').get(pk=turma_id)
            periodo_letivo_id = turma_obj.periodo_letivo_id
            if not num_alunos:
                num_alunos = turma_obj.numero_alunos
        except Turma.DoesNotExist:
            return JsonResponse({'erro': 'Turma não encontrada'}, status=404)

    if not periodo_letivo_id:
        return JsonResponse({
            'conflitos': [],
            'sugestoes_salas': [],
            'sugestoes_horarios': [],
        })

    try:
        num_alunos = int(num_alunos)
    except (ValueError, TypeError):
        num_alunos = 0

    resultado = gerar_sugestoes(
        periodo_letivo_id=periodo_letivo_id,
        professor_id=professor_id,
        sala_id=sala_id,
        horario_id=horario_id,
        turma_id=turma_id,
        num_alunos=num_alunos,
    )

    return JsonResponse(resultado)

def horario_list(request):
    horarios = Horario.objects.all()
    return render(request, 'alocacao/horario_list.html', {'horarios': horarios})


def horario_create(request):
    if request.method == 'POST':
        dia_semana = request.POST.get('dia_semana')
        horario_inicio = request.POST.get('horario_inicio')
        horario_fim = request.POST.get('horario_fim')

        try:
            horario = Horario(
                dia_semana=dia_semana,
                horario_inicio=horario_inicio,
                horario_fim=horario_fim,
                ativo=True,
            )
            horario.full_clean()
            horario.save()
            messages.success(request, "Horário cadastrado com sucesso!")
        except ValidationError as erro:
            if hasattr(erro, "message_dict"):
                mensagens = "; ".join(
                    f"{campo}: {', '.join(msgs)}" for campo, msgs in erro.message_dict.items()
                )
            else:
                mensagens = "; ".join(erro.messages)
            messages.error(request, f"Não foi possível salvar o horário: {mensagens}")
        except IntegrityError:
            messages.error(request, "Já existe um horário cadastrado com esse dia e faixa.")

        return redirect('alocacao:horario_list')

    return redirect('alocacao:horario_list')


def horario_update(request, pk):
    horario = get_object_or_404(Horario, pk=pk)

    if request.method == 'POST':
        horario.dia_semana = request.POST.get('dia_semana')
        horario.horario_inicio = request.POST.get('horario_inicio')
        horario.horario_fim = request.POST.get('horario_fim')
        horario.ativo = request.POST.get('ativo') == 'on'

        try:
            horario.full_clean()
            horario.save()
            messages.success(request, "Horário atualizado com sucesso!")
        except ValidationError as erro:
            if hasattr(erro, "message_dict"):
                mensagens = "; ".join(
                    f"{campo}: {', '.join(msgs)}" for campo, msgs in erro.message_dict.items()
                )
            else:
                mensagens = "; ".join(erro.messages)
            messages.error(request, f"Não foi possível salvar o horário: {mensagens}")
        except IntegrityError:
            messages.error(request, "Já existe um horário cadastrado com esse dia e faixa.")

        return redirect('alocacao:horario_list')

    return redirect('alocacao:horario_list')


def horario_delete(request, pk):
    horario = get_object_or_404(Horario, pk=pk)
    if request.method == 'POST':
        try:
            horario.delete()
            messages.success(request, "Horário excluído com sucesso.")
        except ProtectedError:
            messages.error(
                request,
                f"Não é possível excluir o horário {horario} pois ele possui alocações "
                "vinculadas. Desative-o (edite e desmarque 'ativo') em vez de excluir."
            )
    return redirect('alocacao:horario_list')