from django.urls import path
from . import views

urlpatterns = [
    path('turmas/novo/', views.TurmaCreateView.as_view(), name='turma_create'),
    path('turmas/<int:pk>/editar/', views.TurmaUpdateView.as_view(), name='turma_update'),
    path('turmas/<int:pk>/excluir/', views.TurmaDeleteView.as_view(), name='turma_delete'),
]