from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from .models import Professor
from django.shortcuts import redirect, render
from .models import Turma
from academico.models import Curso, PeriodoLetivo
    
def turma_list(request):

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
                    periodo_instancia = PeriodoLetivo.objects.filter(semestre=semestre_num).first()
        if not periodo_instancia:
            periodo_instancia = PeriodoLetivo.objects.first()
        if not periodo_instancia:
            return render(request, 'pessoas/turma_list.html', {
                'turmas': Turma.objects.all(),
                'cursos': Curso.objects.all(),
                'periodos': PeriodoLetivo.objects.all(),
                'erro': "Não foi possível criar a turma porque não há nenhum Período Letivo cadastrado no banco de dados."
            })
        
        Turma.objects.create(
            nome=nome,
            curso=curso_instancia,
            periodo_letivo=periodo_instancia,
            numero_alunos=numero_alunos if numero_alunos else 1,
            turno=turno
        )
        
        return redirect('/pessoas/turmas/')

    turmas = Turma.objects.all()
    cursos = Curso.objects.all()
    periodos = PeriodoLetivo.objects.all()
    
    return render(request, 'pessoas/turma_list.html', {
        'turmas': turmas,
        'cursos': cursos,
        'periodos': periodos
    })


def turma_update(request, pk):
    turma = Turma.objects.get(pk=pk)
    if request.method == 'POST':
        turma.nome = request.POST.get('nome')
        curso_id = request.POST.get('curso')
        periodo_letivo = request.POST.get('periodo_letivo')
        turma.numero_alunos = request.POST.get('numero_alunos')
        turma.turno = request.POST.get('turno')

        curso_instancia = Curso.objects.get(id=curso_id) if curso_id else None
        periodo_instancia = None

        if periodo_letivo:
            if str(periodo_letivo).isdigit():
                periodo_instancia = PeriodoLetivo.objects.filter(id=periodo_letivo).first()
            else:
                apenas_numeros = ''.join(c for c in str(periodo_letivo) if c.isdigit())
                if apenas_numeros:
                    semestre_num = int(apenas_numeros)
                    periodo_instancia = PeriodoLetivo.objects.filter(semestre=semestre_num).first()

        turma.curso = curso_instancia
        turma.periodo_letivo = periodo_instancia
        turma.save()

def professor_list(request):
    return render(request, 'pessoas/professor_list.html', {})
