from django.shortcuts import render

def alocacao_list(request):
    return render(request, 'alocacao/alocacao_list.html', {})