from django.shortcuts import render, get_object_or_404
from academico.models import PeriodoLetivo
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
