from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from academico.models import Curso, Disciplina, PeriodoLetivo
from pessoas.models import Professor, Turma
from infraestrutura.models import Sala
from alocacao.models import STATUS_ATIVOS_ALOCACAO, Alocacao, Horario 
from alocacao.services.sugestoes import gerar_sugestoes
from rest_framework.views import APIView
from rest_framework.response import Response

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
        periodo_atual = periodos.first()

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
    context_base = {
        'periodos': PeriodoLetivo.objects.all(),
        'professores': Professor.objects.all(),
        'disciplinas': Disciplina.objects.all(),
        'turmas': Turma.objects.all(),
        'salas': Sala.objects.all(),
        'horarios': Horario.objects.all(),
    }

    if request.method == 'POST':
        disciplina_id = request.POST.get('disciplina')
        turma_id = request.POST.get('turma')
        professor_id = request.POST.get('professor')
        sala_id = request.POST.get('sala')
        horario_id = request.POST.get('horario')

        if not all([disciplina_id, turma_id, professor_id, sala_id, horario_id]):
            messages.error(request, 'Erro ao criar alocação!')
            return render(
                request,
                'alocacao/alocacao_list.html',
                {**context_base, 'erro': 'Preencha todos os campos obrigatórios.'},
            )

        periodo_id = None

        if turma_id:
            try:
                turma_obj = Turma.objects.get(pk=turma_id)
                periodo_id = turma_obj.periodo_letivo.id
            except Turma.DoesNotExist:
                messages.error(request, 'Erro ao criar alocação!')
                return render(
                    request,
                    'alocacao/alocacao_list.html',
                    {**context_base, 'erro': 'Turma informada não existe.'},
                )

        try:
            alocacao = Alocacao.objects.create(
                disciplina_id=disciplina_id,
                turma_id=turma_id,
                professor_id=professor_id,
                sala_id=sala_id,
                horario_id=horario_id,
                periodo_letivo_id=periodo_id,
            )
            messages.success(request, 'Alocação criada com sucesso!')
            return redirect('grade_horaria')

        except Exception as exc:
            messages.error(request, 'Erro ao criar alocação!')
            return render(
                request,
                'alocacao/alocacao_list.html',
                {**context_base, 'erro': f'Erro ao salvar: {exc}'},
            )

    ultima_turma = Turma.objects.order_by('-id').first()
    semestre_atual = ultima_turma.periodo_letivo if ultima_turma else "2026.2"
    context_base['semestre_atual'] = semestre_atual

    return render(request, 'alocacao/alocacao_list.html', context_base)

def dashboard_view(request):
    return render(request, 'alocacao/dashboard.html')

def dashboard_data_api(request):
    try:
        total_alocacoes = Alocacao.objects.count()
        #conflitos_pendentes = Conflito.objects.filter(resolvido=False).count()
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
        #salas_alocadas = 38
        #salas_livres = 8
        #salas_manutencao = 3

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
    # Fallback para caso ainda existam strings gravadas temporariamente no banco
    '1': 'segunda', '2': 'terca', '3': 'quarta', '4': 'quinta', '5': 'sexta', '6': 'sabado',
    'segunda': 'segunda', 'terca': 'terca', 'quarta': 'quarta', 'quinta': 'quinta', 'sexta': 'sexta',
    'terça': 'terca'
}

HORARIOS_GRID = [
    '08:00', '09:00', '10:00', '11:00', '12:00',
    '13:00', '14:00', '15:00', '16:00', '17:00'
]


def normalizar_horario(horario_obj):
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


def classificar_alocacao(alocacao, todas_alocacoes):
    if alocacao.turma.numero_alunos > alocacao.sala.capacidade_alunos:
        return 'aviso'

    conflito_professor = [
        a for a in todas_alocacoes
        if a.pk != alocacao.pk
        and a.professor_id == alocacao.professor_id
        and a.horario_id == alocacao.horario_id
        and a.status in STATUS_ATIVOS_ALOCACAO
    ]
    if conflito_professor:
        return 'critico'

    conflito_turma = [
        a for a in todas_alocacoes
        if a.pk != alocacao.pk
        and a.turma_id == alocacao.turma_id
        and a.horario_id == alocacao.horario_id
        and a.status in STATUS_ATIVOS_ALOCACAO
    ]
    if conflito_turma:
        return 'critico'

    return None


def grade_horaria_view(request):
    dias_semana_colunas = ['segunda', 'terca', 'quarta', 'quinta', 'sexta']

    curso_id = request.GET.get('curso')
    
    alocacoes_qs = Alocacao.objects.select_related(
        'disciplina', 'turma', 'professor', 'sala', 'periodo_letivo', 'horario'
    )

    if curso_id and curso_id != '' and curso_id != 'todos':
        alocacoes_qs = alocacoes_qs.filter(disciplina__curso_id=curso_id)

    alocacoes = list(alocacoes_qs.all())

    print(f"\n[DEBUG] TOTAL DE ALOCAÇÕES ENCONTRADAS NO BANCO: {len(alocacoes)}")

    matriz_grade = {
        hora: {dia: [] for dia in dias_semana_colunas}
        for hora in HORARIOS_GRID
    }

    for alocacao in alocacoes:
        if not alocacao.horario:
            print(f"[DEBUG] Alocação ID {alocacao.pk} ignorada: Sem horário associado.")
            continue

        alocacao.tipo_conflito = classificar_alocacao(alocacao, alocacoes)
        alocacao.tem_conflito = alocacao.tipo_conflito == 'critico'

        dia_num = alocacao.horario.dia_semana
        dia_coluna = DIAS_MAPA.get(dia_num, str(dia_num).lower().strip())
        
        hora_inicio = alocacao.horario.horario_inicio
        slot_horario = normalizar_horario(hora_inicio)

        print(f"[DEBUG] Hora no banco: '{hora_inicio}' -> Mapeada para slot: '{slot_horario}' | Dia no banco: '{dia_num}' (Coluna: '{dia_coluna}')")

        if slot_horario in matriz_grade and dia_coluna in matriz_grade[slot_horario]:
            matriz_grade[slot_horario][dia_coluna].append(alocacao)
            print("  '--> MATCH ENCONTRADO! Alocacao adicionada.")
        else:
            print("  '--> NÃO DEU MATCH!")

    linhas_grade = []
    for hora in HORARIOS_GRID:
        linha = {
            'hora': hora,
            'celulas': [
                {
                    'dia': dia,
                    'alocacoes': matriz_grade[hora][dia]
                }
                for dia in dias_semana_colunas
            ]
        }
        linhas_grade.append(linha)

    total_conflitos = sum(
        1 for a in alocacoes
        if getattr(a, 'tipo_conflito', None) == 'critico'
    )

    cursos_banco = Curso.objects.all()

    context = {
        'linhas_grade': linhas_grade,
        'dias_semana': dias_semana_colunas,
        'horarios_grid': HORARIOS_GRID,
        'cursos': cursos_banco,            
        'curso_selecionado': curso_id,
        'total_conflitos': total_conflitos,
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