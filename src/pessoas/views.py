from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from .models import Professor

def professor_list(request):
    return render(request, 'pessoas/professor_list.html', {})
class ProfessorCreateView(CreateView):
    model = Professor
    fields = '__all__'
    success_url = reverse_lazy('professor_create')

class ProfessorUpdateView(UpdateView):
    model = Professor
    fields = '__all__'
    context_object_name = 'professor'
    success_url = reverse_lazy('professor_create')

class ProfessorDeleteView(DeleteView):
    model = Professor
    context_object_name = 'professor'
    success_url = reverse_lazy('professor_create')
