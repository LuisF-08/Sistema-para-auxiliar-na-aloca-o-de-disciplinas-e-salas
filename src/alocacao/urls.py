from django.urls import path
from . import views

app_name = 'alocacao'

urlpatterns = [
    path('', views.alocacao_list, name='alocacao_list'),
]