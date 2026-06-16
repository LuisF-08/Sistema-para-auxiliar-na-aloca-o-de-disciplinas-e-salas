from django.urls import path
from . import views

urlpatterns = [
    path('professores/novo/', views.ProfessorCreateView.as_view(), name='professor_create'),
    path('professores/<int:pk>/editar/', views.ProfessorUpdateView.as_view(), name='professor_update'),
    path('professores/<int:pk>/excluir/', views.ProfessorDeleteView.as_view(), name='professor_delete'),
]