from django.urls import path
from . import views

app_name = 'academico'

urlpatterns = [
    path('disciplinas/', views.disciplina_list, name='disciplina_list'),
    path('disciplinas/nova/', views.disciplina_create, name='disciplina_create'),
    path('disciplinas/<int:pk>/update/', views.disciplina_update, name='disciplina_update'),
    path('disciplinas/<int:pk>/delete/', views.disciplina_delete, name='disciplina_delete'),
    path('cursos/', views.curso_list, name='curso_list'),
    path('cursos/novo/', views.curso_create, name='curso_create'),
    path('cursos/<int:pk>/editar/', views.curso_update, name='curso_update'),
    path('cursos/<int:pk>/excluir/', views.curso_delete, name='curso_delete'),
]