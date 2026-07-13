from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from .models import Sala


def sala_list(request):

    lista_de_salas = Sala.objects.all() 
    return render(request, 'infraestrutura/sala_list.html', {'salas': lista_de_salas})

def sala_create(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        localizacao = request.POST.get('localizacao')
        tipo_sala = request.POST.get('tipo_sala')
        capacidade_alunos = request.POST.get('capacidade_alunos')
        try:
            Sala.objects.create(
                nome=nome,
                localizacao=localizacao,
                tipo_sala=tipo_sala,
                capacidade_alunos=int(capacidade_alunos) if capacidade_alunos else 1,
            )
            messages.success(request, 'Sala cadastrada com sucesso!') 
        except IntegrityError:
            messages.error(request, f'Já existe uma sala cadastrada com o nome "{nome}".') 

        return redirect('infraestrutura:sala_list')

    return redirect('infraestrutura:sala_list')


def sala_update(request, pk):
    sala = get_object_or_404(Sala, pk=pk)
   
    if request.method == 'POST':
        sala.nome = request.POST.get('nome')
        sala.localizacao = request.POST.get('localizacao')
        sala.tipo_sala = request.POST.get('tipo_sala')
        capacidade_alunos = request.POST.get('capacidade_alunos')
        sala.capacidade_alunos = int(capacidade_alunos) if capacidade_alunos else 1

        try:
            sala.save()
            messages.success(request, 'Sala atualizada com sucesso!')
        except IntegrityError:
            messages.error(request, f'Já existe uma sala cadastrada com o nome "{sala.nome}".')

        return redirect('infraestrutura:sala_list')

    return redirect('infraestrutura:sala_list')

def sala_delete(request, pk):
    sala = get_object_or_404(Sala, pk=pk)
    if request.method == 'POST':
        sala.delete()
        messages.success(request, 'Sala excluída com sucesso!')
        return redirect('infraestrutura:sala_list')
    return render(request, 'infraestrutura/sala_confirm_delete.html', {'sala': sala})