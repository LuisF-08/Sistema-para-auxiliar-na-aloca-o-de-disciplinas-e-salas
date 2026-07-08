from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from .models import Professor

def professor_list(request):
    professores = Professor.objects.all()
    return render(request, 'pessoas/professor_list.html', {'professores': professores})
class ProfessorCreateView(CreateView):
    model = Professor
    fields = '__all__'
    success_url = reverse_lazy('pessoas:professor_create')

class ProfessorUpdateView(UpdateView):
    model = Professor
    fields = '__all__'
    context_object_name = 'professor'
    success_url = reverse_lazy('pessoas:professor_create')

class ProfessorDeleteView(DeleteView):
    model = Professor
    context_object_name = 'professor'
    success_url = reverse_lazy('pessoas:professor_create')
