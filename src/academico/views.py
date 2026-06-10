from django.shortcuts import render
from .models import Disciplina

def disciplina_list(request):
    disciplinas = Disciplina.objects.all()
    return render(request, 'academico/disciplina_list.html', {'disciplinas': disciplinas})