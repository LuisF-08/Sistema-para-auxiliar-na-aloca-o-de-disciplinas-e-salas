from django.urls import path
from . import views

app_name = 'academico'

urlpatterns = [
    path('disciplinas/', views.disciplina_list, name='disciplina_list'),
]