from django.urls import path
from . import views

app_name = 'infraestrutura'

urlpatterns = [
    path('salas/', views.sala_list, name='sala_list'),
    path('salas/novo/', views.sala_create, name='sala_create'),
    path('salas/<int:pk>/editar/', views.sala_update, name='sala_update'),
    path('salas/<int:pk>/excluir/', views.sala_delete, name='sala_delete')
]