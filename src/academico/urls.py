from django.urls import path
from . import views

app_name = 'academico'

urlpatterns = [
    path('disciplinas/', views.disciplina_list, name='disciplina_list'),
    path('disciplinas/nova/', views.disciplina_create, name='disciplina_create'),
    path('disciplinas/<int:pk>/update/', views.disciplina_update, name='disciplina_update'),
    path('disciplinas/<int:pk>/delete/', views.disciplina_delete, name='disciplina_delete'),
]