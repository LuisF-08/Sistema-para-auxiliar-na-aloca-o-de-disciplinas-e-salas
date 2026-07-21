from django.urls import path
from . import views

app_name = 'alocacao'

urlpatterns = [
    path('', views.dashboard_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/api/dados/', views.dashboard_data_api, name='dashboard_data_api'),
]