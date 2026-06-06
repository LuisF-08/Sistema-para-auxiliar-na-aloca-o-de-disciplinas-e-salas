from django.urls import path
from . import views

app_name = 'academico'

urlpatterns = [
    path('cursos/', views.curso_list, name='curso_list'),
]