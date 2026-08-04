from django.db import IntegrityError
from django.db.models import Count, ProtectedError
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from .models import Turma, Professor
from academico.models import Curso, PeriodoLetivo


def turma_create(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        curso_id = request.POST.get('curso')
        periodo_letivo = request.POST.get('periodo_letivo')
        numero_alunos = request.POST.get('numero_alunos')
        turno = request.POST.get('turno')

        curso_instancia = Curso.objects.get(id=curso_id) if curso_id else None

        periodo_instancia = None
        if periodo_letivo:
            if str(periodo_letivo).isdigit():
                periodo_instancia = PeriodoLetivo.objects.filter(id=periodo_letivo).first()
            else:
                apenas_numeros = ''.join(c for c in str(periodo_letivo) if c.isdigit())
                if apenas_numeros:
                    semestre_num = int(apenas_numeros)
                    periodo_instancia = PeriodoLetivo.objects.filter(
                        semestre=semestre_num, ativo=True,
                    ).first()
        if not periodo_instancia:
            periodo_instancia = PeriodoLetivo.atual()
        if not periodo_instancia:
            return render(request, 'pessoas/turma_list.html', {
                'turmas': Turma.objects.all(),
                'cursos': Curso.objects.all(),
                'periodos': PeriodoLetivo.objects.filter(ativo=True),
                'erro': "Não foi possível criar a turma porque não há nenhum Período Letivo ativo cadastrado no banco de dados."
            })

        try:
            Turma.objects.create(
                nome=nome,
                curso=curso_instancia,
                periodo_letivo=periodo_instancia,
                numero_alunos=numero_alunos if numero_alunos else 1,
                turno=turno
            )
            messages.success(request, 'Turma cadastrada com sucesso!')
        except IntegrityError:
            messages.error(request, f'Já existe uma turma cadastrada com o nome "{nome}" para este curso e período.')

        return redirect('pessoas:turma_list')

    turmas = Turma.objects.all()
    cursos = Curso.objects.all()
    periodos = PeriodoLetivo.objects.filter(ativo=True)

    return render(request, 'pessoas/turma_list.html', {
        'turmas': turmas,
        'cursos': cursos,
        'periodos': periodos
    })


def turma_list(request):
    turmas = Turma.objects.all()
    cursos = Curso.objects.all()
    periodos = PeriodoLetivo.objects.all()

    return render(request, 'pessoas/turma_list.html', {
        'turmas': turmas,
        'cursos': cursos,
        'periodos': periodos
    })


def turma_update(request, pk):
    turma = get_object_or_404(Turma, pk=pk)

    if request.method == 'POST':
        turma.nome = request.POST.get('nome')
        curso_id = request.POST.get('curso')
        periodo_id = request.POST.get('periodo_letivo')
        numero_alunos = request.POST.get('numero_alunos')
        turma.turno = request.POST.get('turno')

        turma.curso = get_object_or_404(Curso, pk=curso_id) if curso_id else None
        turma.periodo_letivo = get_object_or_404(PeriodoLetivo, pk=periodo_id) if periodo_id else None
        turma.numero_alunos = int(numero_alunos) if numero_alunos else 0

        try:
            turma.save()
            messages.success(request, 'Turma atualizada com sucesso!')
        except IntegrityError:
            messages.error(
                request,
                f'Já existe uma turma cadastrada com o nome "{turma.nome}" para este curso e período.'
            )

        return redirect('pessoas:turma_list')

    return redirect('pessoas:turma_list')


def turma_delete(request, pk):
    turma = get_object_or_404(Turma, pk=pk)
    if request.method == 'POST':
        try:
            turma.delete()
            messages.success(request, 'Turma excluída com sucesso!')
        except ProtectedError:
            messages.error(
                request,
                f'Não é possível excluir a turma "{turma.nome}" pois ela possui alocações vinculadas.'
            )
    return redirect('pessoas:turma_list')


def professor_list(request):
    mostrar_inativos = request.GET.get('mostrar_inativos') == '1'
    professores = Professor.objects.all() if mostrar_inativos else Professor.objects.filter(ativo=True)
    professores = professores.annotate(alocacoes_count=Count('alocacoes'))
    return render(request, 'pessoas/professor_list.html', {
        'professores': professores,
        'mostrar_inativos': mostrar_inativos,
    })


def professor_create(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        especialidade = request.POST.get('especialidade')
        carga_horaria_maxima = request.POST.get('cargaHorariaMaxima')
        ativo = request.POST.get('ativo') == 'on'
        try:
            Professor.objects.create(
                nome=nome,
                email=email,
                especialidade=especialidade,
                carga_horaria_maxima=int(carga_horaria_maxima) if carga_horaria_maxima else None,
                ativo=ativo
            )
            messages.success(request, 'Professor cadastrado com sucesso!')
        except IntegrityError:
            messages.error(request, f'Já existe um professor cadastrado com o e-mail "{email}".')

        return redirect('pessoas:professor_list')

    professores = Professor.objects.all()

    return render(request, 'pessoas/professor_list.html', {
        'professores': professores
    })


def professor_update(request, pk):
    professor = get_object_or_404(Professor, pk=pk)

    if request.method == 'POST':
        professor.nome = request.POST.get('nome')
        professor.email = request.POST.get('email')
        professor.especialidade = request.POST.get('especialidade')
        carga_horaria_maxima = request.POST.get('cargaHorariaMaxima')
        professor.carga_horaria_maxima = int(carga_horaria_maxima) if carga_horaria_maxima else 10
        professor.ativo = request.POST.get('ativo') == 'on'

        try:
            professor.save()
            messages.success(request, 'Professor atualizado com sucesso!')
        except IntegrityError:
            messages.error(request, f'Já existe um professor cadastrado com o e-mail "{professor.email}".')

        return redirect('pessoas:professor_list')

    return render(request, 'pessoas/professor_form.html', {'professor': professor})


def professor_delete(request, pk):
    professor = get_object_or_404(Professor, pk=pk)
    if request.method == 'POST':
        try:
            professor.delete()
            messages.success(request, f'Professor {professor.nome} excluído com sucesso.')
        except ProtectedError:
            messages.error(
                request,
                f'Não é possível excluir o professor "{professor.nome}" pois ele possui alocações vinculadas.'
            )
        return redirect('pessoas:professor_list')

    return redirect('pessoas:professor_list')
