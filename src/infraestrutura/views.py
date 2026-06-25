from django.shortcuts import render
from .models import Sala


def sala_list(request):

    lista_de_salas = Sala.objects.all() 
    return render(request, 'infraestrutura/sala_list.html', {'salas': lista_de_salas})