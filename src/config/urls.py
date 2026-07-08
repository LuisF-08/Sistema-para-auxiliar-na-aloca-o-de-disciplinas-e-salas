"""Root URL configuration."""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('academico/', include('academico.urls', namespace='academico')),
    path('pessoas/', include('pessoas.urls', namespace='pessoas')),
    path('infraestrutura/', include('infraestrutura.urls', namespace='infraestrutura')),
    path('alocacao/', include('alocacao.urls', namespace='alocacao')),
    path('relatorios/', include('relatorios.urls', namespace='relatorios')),
    path('api/', include('api.urls')),  # api rest (viewsets ja existiam mas n tavam conectadas)
]

