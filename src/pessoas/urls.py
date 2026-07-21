from django.urls import path
from . import views

app_name = 'pessoas'

urlpatterns = [
    path('turmas/', views.turma_list, name='turma_list'),
    path('turmas/nova/', views.turma_create, name='turma_create'),
    path('turmas/<int:pk>/editar/', views.turma_update, name='turma_update'),
    path('turmas/<int:pk>/excluir/', views.turma_delete, name='turma_delete'),

    path('professores/', views.professor_list, name='professor_list'),
    path('professores/nova/', views.professor_create, name='professor_create'),
    path('professores/<int:pk>/editar/', views.professor_update, name='professor_update'),
    path('professores/<int:pk>/excluir/', views.professor_delete, name='professor_delete'),
]