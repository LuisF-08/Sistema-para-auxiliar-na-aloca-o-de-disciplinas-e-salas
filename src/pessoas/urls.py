from django.urls import path
from . import views

app_name = 'pessoas'

urlpatterns = [
    path('professores/', views.professor_list, name='professor_list'),
]