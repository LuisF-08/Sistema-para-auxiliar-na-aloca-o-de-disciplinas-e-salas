from django.urls import path
from . import views

app_name = 'pessoas'

urlpatterns = [
    path('turmas/', views.turma_list, name='turma_list'),
    path('professores/', views.professor_list, name='professor_list'),
]