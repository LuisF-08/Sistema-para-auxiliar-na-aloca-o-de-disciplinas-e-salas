
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.db.models import Count
from academico.models import Disciplina, Curso, PeriodoLetivo
from pessoas.models import Professor, Turma
from infraestrutura.models import Sala
from django.db.models import Q
from alocacao.models import Alocacao 

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
    }
    
    return render(request, 'alocacao/alocacao_list.html', context)


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

def grade_horaria_view(request):

   # Lista de horários fixos da tabela
    horarios = ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]
    
    # 1. Ajustado para bater exatamente com o 'Terca' sem cedilha do seu banco
    dias_semana = ["Segunda", "Terca", "Quarta", "Quinta", "Sexta"]
    
    # Para exibição amigável no cabeçalho do HTML, se quiser:
    dias_display = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]

    curso_id = request.GET.get('curso')
    cursos = Curso.objects.all()

    alocacoes_qs = Alocacao.objects.select_related('disciplina', 'professor', 'sala', 'turma', 'horario').all()
    
    if curso_id:
        alocacoes_qs = alocacoes_qs.filter(turma__curso_id=curso_id)

    matriz_grade = {h: {d: None for d in dias_semana} for h in horarios} 

    print(f"--> TOTAL DE ALOCAÇÕES ENCONTRADAS NO BANCO: {alocacoes_qs.count()}")

    for alocacao in alocacoes_qs:
        if alocacao.horario:
            hora_inicio = alocacao.horario.horario_inicio
            
            # Encontra o slot de hora correto (ex: 08:40 pega o slot das 08:00)
            hora_slot = f"{hora_inicio.hour:02d}:00"
            
            # Extrai o dia da semana exatamente como o Django devolve
            dia_str = str(alocacao.horario.get_dia_semana_display()).split('-')[0].capitalize()

            print(f"[DEBUG] Hora no banco: '{hora_inicio.strftime('%H:%M')}' -> Mapeado para slot: '{hora_slot}' | Dia no banco: '{dia_str}'")

            if hora_slot in matriz_grade and dia_str in matriz_grade[hora_slot]:
                matriz_grade[hora_slot][dia_str] = alocacao
                print("   └--> MATCH ENCONTRADO! Alocação adicionada.")
            else:
                print("   └--> NÃO DEU MATCH!")

    linhas_grade = []
    for hora in horarios:
        linha = {'hora': hora, 'celulas': []}
        for dia in dias_semana:
            linha['celulas'].append(matriz_grade[hora][dia])
        linhas_grade.append(linha)

    context = {
        'horarios': horarios,
        'dias_semana': dias_display, 
        'linhas_grade': linhas_grade,  
        'cursos': cursos,
        'curso_selecionado': curso_id,
        'total_conflitos': 0
    }

    return render(request, 'alocacao/grade_horaria.html', context)
