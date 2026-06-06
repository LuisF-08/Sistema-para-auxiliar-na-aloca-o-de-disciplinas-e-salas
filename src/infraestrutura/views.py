from django.shortcuts import render

def sala_list(request):
    return render(request, 'infraestrutura/sala_list.html', {})