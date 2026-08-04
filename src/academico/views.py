from django.db import IntegrityError
from django.db.models import ProtectedError
from django.shortcuts import redirect, render, get_object_or_404
from django.core.exceptions import ValidationError
from .models import Disciplina, Curso, PeriodoLetivo
from django.contrib import messages

def disciplina_list(request):
    disciplinas = Disciplina.objects.select_related('curso').all()
    cursos = Curso.objects.all()
    return render(request, 'academico/disciplina_list.html', {
        'disciplinas': disciplinas,
        'cursos': cursos,
    })


def disciplina_create(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        codigo = request.POST.get('codigo')
        carga_horaria = request.POST.get('carga_horaria_semanal')
        periodo_rec = request.POST.get('periodo')
        curso_id = request.POST.get('curso')
        
        if not curso_id:
            messages.error(request, 'É necessário selecionar um Curso para cadastrar a disciplina.')
            return redirect('academico:disciplina_list')

        curso_instancia = Curso.objects.filter(id=curso_id).first()
        
        if not curso_instancia:
            messages.error(request, 'O curso selecionado não existe.')
            return redirect('academico:disciplina_list')

        try:
            Disciplina.objects.create(
                nome=nome,
                codigo=codigo,
                carga_horaria_semanal=carga_horaria if carga_horaria else 1,
                periodo_recomendado=periodo_rec if periodo_rec else None,
                curso=curso_instancia
            )
            messages.success(request, 'Disciplina criada com sucesso!')
        except IntegrityError:
            messages.error(
                request, 
                f'Já existe uma disciplina cadastrada com o código "{codigo}" ou nome "{nome}" para este curso.'
            )

    return redirect('academico:disciplina_list') 

def disciplina_update(request, pk):
    disciplina = get_object_or_404(Disciplina, pk=pk)
    
    if request.method == 'POST':
        disciplina.nome = request.POST.get('nome')
        disciplina.codigo = request.POST.get('codigo')
        disciplina.carga_horaria_semanal = request.POST.get('carga_horaria_semanal')
        disciplina.periodo_recomendado = request.POST.get('periodo') or None
        curso_id = request.POST.get('curso')
        disciplina.curso = Curso.objects.filter(id=curso_id).first() if curso_id else None
        
        try:
            disciplina.save()
            messages.success(request, 'Disciplina atualizada com sucesso!')
        except IntegrityError:
            messages.error(request, f'Já existe uma disciplina cadastrada com o código "{disciplina.codigo}" ou nome "{disciplina.nome}" para o curso selecionado.')
        
        return redirect('academico:disciplina_list')
    
    return render(request, 'academico/disciplina_update.html', {'disciplina': disciplina})

def disciplina_delete(request, pk):
    disciplina = get_object_or_404(Disciplina, pk=pk)
    
    if request.method == 'POST':
        disciplina.delete()
        messages.success(request, 'Disciplina excluída com sucesso!')
        return redirect('academico:disciplina_list')
    
    return render(request, 'academico/disciplina_confirm_delete.html', {'disciplina': disciplina})

def curso_list(request):
    cursos = Curso.objects.all()
    return render (request, 'academico/curso_list.html', {'cursos': cursos})

def curso_create(request):
    if request.method == 'POST':
        curso_id = request.POST.get('curso_id')
        nome = request.POST.get('nome')
        codigo = request.POST.get('codigo')
        
        if curso_id:
            curso = get_object_or_404(Curso, id=curso_id)
            curso.nome = nome
            curso.codigo = codigo
            curso.save()
            messages.success(request, "Curso atualizado com sucesso!")
        else:
            if nome:
                Curso.objects.create(nome=nome, codigo=codigo)
                messages.success(request, "Curso cadastrado com sucesso!")
            else:
                messages.error(request, "O nome do curso é obrigatório.")
        
        return redirect('academico:curso_list')

    cursos = Curso.objects.all()
    return render(request, 'academico/curso_list.html', {'cursos': cursos})

def curso_update(request, pk):
    curso = get_object_or_404(Curso, pk=pk)
    if request.method == 'POST':
        curso.nome = request.POST.get('nome')
        curso.codigo = request.POST.get('codigo')
        try:
            curso.save()
            messages.success(request, "Curso atualizado com sucesso!")
        except IntegrityError:
            messages.error(
                request,
                f'Já existe um curso cadastrado com o código "{curso.codigo}" ou nome "{curso.nome}".'
            )
    return redirect('academico:curso_list')

def curso_delete(request, pk):
    curso = get_object_or_404(Curso, pk=pk)
    if request.method == 'POST':
        try:
            curso.delete()
            messages.success(request, "Curso excluído com sucesso.")
        except ProtectedError:
            messages.error(request, "Não é possível excluir este curso pois ele possui disciplinas ou turmas vinculadas.")
    return redirect('academico:curso_list')


def periodo_list(request):
    periodos = PeriodoLetivo.objects.all().order_by('-ano', '-semestre')
    return render(request, 'academico/periodo_list.html', {'periodos': periodos})


def periodo_create(request):
    """cria um novo periodo letivo ou atualiza um existente (via periodo_id no POST)."""
    if request.method == 'POST':
        periodo_id = request.POST.get('periodo_id')
        ano = request.POST.get('ano')
        semestre = request.POST.get('semestre')
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')

        try:
            if periodo_id:
                periodo = get_object_or_404(PeriodoLetivo, pk=periodo_id)
                periodo.ano = ano
                periodo.semestre = semestre
                periodo.data_inicio = data_inicio
                periodo.data_fim = data_fim
                periodo.full_clean()
                periodo.save()
                messages.success(request, "Período letivo atualizado com sucesso!")
            else:
                novo_periodo = PeriodoLetivo(
                    ano=ano,
                    semestre=semestre,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    ativo=True,
                )
                novo_periodo.full_clean()
                novo_periodo.save()
                messages.success(
                    request,
                    f"Semestre {novo_periodo} criado! Os períodos anteriores continuam "
                    "salvos e disponíveis para consulta e histórico."
                )
        except ValidationError as erro:
            if hasattr(erro, "message_dict"):
                mensagens = "; ".join(
                    f"{campo}: {', '.join(msgs)}" for campo, msgs in erro.message_dict.items()
                )
            else:
                mensagens = "; ".join(erro.messages)
            messages.error(request, f"Não foi possível salvar o período: {mensagens}")
        except IntegrityError:
            messages.error(
                request,
                f"Já existe um período letivo cadastrado para {ano}.{semestre}."
            )

        return redirect('academico:periodo_list')

    return redirect('academico:periodo_list')


def periodo_arquivar(request, pk):
    """'exclui' o periodo sem apagar do banco: so marca como inativo.

    o periodo some da lista de periodos ativos (usada em turma_create,
    dashboards e relatorios), mas continua no banco pra fins de
    busca/historico — turmas e alocacoes antigas continuam intactas.
    """
    periodo = get_object_or_404(PeriodoLetivo, pk=pk)
    if request.method == 'POST':
        periodo.ativo = False
        periodo.save()
        messages.success(
            request,
            f"Período {periodo} arquivado. Ele não aparece mais como período "
            "corrente, mas continua disponível para relatórios e histórico."
        )
    return redirect('academico:periodo_list')


def periodo_reativar(request, pk):
    """reverte o arquivamento, caso precise voltar um periodo antigo a ficar ativo."""
    periodo = get_object_or_404(PeriodoLetivo, pk=pk)
    if request.method == 'POST':
        periodo.ativo = True
        periodo.save()
        messages.success(request, f"Período {periodo} reativado.")
    return redirect('academico:periodo_list')


def periodo_delete(request, pk):
    """exclusao definitiva do periodo — so funciona se nao houver turma ou
    alocacao vinculada (PROTECT no banco). pra manter o historico, prefira
    'arquivar' em vez de excluir de verdade."""
    periodo = get_object_or_404(PeriodoLetivo, pk=pk)
    if request.method == 'POST':
        try:
            periodo.delete()
            messages.success(request, "Período letivo excluído com sucesso.")
        except ProtectedError:
            messages.error(
                request,
                f"Não é possível excluir o período {periodo} pois ele possui turmas "
                "ou alocações vinculadas. Use a opção \"Arquivar\" para tirá-lo da "
                "lista de períodos ativos sem perder o histórico."
            )
    return redirect('academico:periodo_list')