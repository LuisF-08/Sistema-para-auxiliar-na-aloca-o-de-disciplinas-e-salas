from django.shortcuts import render
from .models import Disciplina
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from pessoas.models import Turma

def disciplina_list(request):
    disciplinas = Disciplina.objects.all()
    return render(request, 'academico/disciplina_list.html', {'disciplinas': disciplinas})

