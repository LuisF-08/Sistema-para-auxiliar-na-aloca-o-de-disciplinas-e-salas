from django.db import IntegrityError
from django.shortcuts import redirect, render, get_object_or_404
from .models import Disciplina, Curso
from django.contrib import messages

def disciplina_list(request):
    disciplinas = Disciplina.objects.all()
    return render(request, 'academico/disciplina_list.html', {'disciplinas': disciplinas})


def disciplina_create(request):
  if request.method == 'POST':
        nome = request.POST.get('nome')
        codigo = request.POST.get('codigo')
        carga_horaria = request.POST.get('carga_horaria_semanal')
        periodo_rec = request.POST.get('periodo_recomendado')
        curso_id = request.POST.get('curso')
        
        curso_instancia = Curso.objects.filter(id=curso_id).first() if curso_id else None
        
        Disciplina.objects.create(
            nome=nome,
            codigo=codigo,
            carga_horaria_semanal=carga_horaria if carga_horaria else 1,
            periodo_recomendado=periodo_rec if periodo_rec else None,
            curso=curso_instancia
        )
  return redirect('/academico/disciplinas/')  

def disciplina_update(request, pk):
    disciplina = get_object_or_404(Disciplina, pk=pk)
    
    if request.method == 'POST':
        disciplina.nome = request.POST.get('nome')
        disciplina.codigo = request.POST.get('codigo')
        disciplina.carga_horaria_semanal = request.POST.get('carga_horaria_semanal')
        disciplina.periodo_recomendado = request.POST.get('periodo_recomendado') or None
        curso_id = request.POST.get('curso')
        disciplina.curso = Curso.objects.filter(id=curso_id).first() if curso_id else None
        
        try:
            disciplina.save()
            messages.success(request, 'Disciplina atualizada com sucesso!')
        except IntegrityError:
            messages.error(request, f'Já existe uma disciplina cadastrada com o código "{disciplina.codigo}" ou nome "{disciplina.nome}" para o curso selecionado.')
        
        return redirect('/academico/disciplinas/')
    
    return render(request, 'academico/disciplina_update.html', {'disciplina': disciplina})

def disciplina_delete(request, pk):
    disciplina = get_object_or_404(Disciplina, pk=pk)
    
    if request.method == 'POST':
        disciplina.delete()
        messages.success(request, 'Disciplina excluída com sucesso!')
        return redirect('/academico/disciplinas/')
    
    return render(request, 'academico/disciplina_confirm_delete.html', {'disciplina': disciplina})

