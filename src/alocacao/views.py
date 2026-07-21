
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.db.models import Count
from academico.models import Disciplina, Curso, PeriodoLetivo
from pessoas.models import Professor, Turma
from alocacao.models import Alocacao
from infraestrutura.models import Sala

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
             qtd = Alocacao.objects.filter(dia_semana=dia).count()
             percentual = int((qtd / total_salas) * 100) if total_salas > 0 else 0
             dados_ocupacao_dias.append(percentual)
        dados_ocupacao_dias = [80, 95, 75, 88, 65]

        salas_alocadas = Alocacao.objects.values('sala').distinct().count()
        salas_manutencao = Sala.objects.filter(status='manutencao').count()
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



