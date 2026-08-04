from django.urls import path
from . import views

app_name = 'alocacao'

urlpatterns = [
    path('alocacoes/', views.alocacao_list, name='alocacoes'),
    path('alocacoes/create/', views.alocacao_create, name='alocacao_create'),
    path('', views.dashboard_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/api/dados/', views.dashboard_data_api, name='dashboard_data_api'),
    path('grade-horaria/', views.grade_horaria_view, name='grade_horaria'),
    path('api/sugestoes/', views.sugestoes_conflito_api, name='sugestoes_conflito'),

    path('horarios/', views.horario_list, name='horario_list'),
    path('horarios/novo/', views.horario_create, name='horario_create'),
    path('horarios/<int:pk>/editar/', views.horario_update, name='horario_update'),
    path('horarios/<int:pk>/excluir/', views.horario_delete, name='horario_delete'),
]