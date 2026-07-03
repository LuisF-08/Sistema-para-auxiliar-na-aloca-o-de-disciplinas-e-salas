from django.urls import path
from . import views

app_name = 'pessoas'

urlpatterns = [
    path('turmas/', views.turma_list, name='turma_list'),
    path('professores/', views.professor_list, name='professor_list'),
    path('professores/novo/', views.ProfessorCreateView.as_view(), name='professor_create'),
    path('professores/<int:pk>/editar/', views.ProfessorUpdateView.as_view(), name='professor_update'),
    path('professores/<int:pk>/excluir/', views.ProfessorDeleteView.as_view(), name='professor_delete'),
]