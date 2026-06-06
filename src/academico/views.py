from django.shortcuts import render

def curso_list(request):
    return render(request, 'academico/curso_list.html', {})