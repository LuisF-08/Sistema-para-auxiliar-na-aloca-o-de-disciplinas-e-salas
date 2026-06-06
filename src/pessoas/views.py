from django.shortcuts import render

def professor_list(request):
    return render(request, 'pessoas/professor_list.html', {})