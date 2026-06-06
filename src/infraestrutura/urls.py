from django.urls import path
from . import views

app_name = 'infraestrutura'

urlpatterns = [
    path('salas/', views.sala_list, name='sala_list'),
]