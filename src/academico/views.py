from django.shortcuts import render
from .models import Disciplina
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from pessoas.models import Turma

def disciplina_list(request):
    disciplinas = Disciplina.objects.all()
    return render(request, 'academico/disciplina_list.html', {'disciplinas': disciplinas})

class TurmaCreateView(CreateView):
    model = Turma
    fields = '__all__'
    template_name = 'academico/turma_form.html'
    success_url = reverse_lazy('turma_create')

class TurmaUpdateView(UpdateView):
    model = Turma
    fields = '__all__'
    context_object_name = 'turma'
    template_name = 'academico/turma_form.html'
    success_url = reverse_lazy('turma_create')

class TurmaDeleteView(DeleteView):
    model = Turma
    context_object_name = 'turma'
    template_name = 'academico/turma_confirm_delete.html'
    success_url = reverse_lazy('turma_create')
