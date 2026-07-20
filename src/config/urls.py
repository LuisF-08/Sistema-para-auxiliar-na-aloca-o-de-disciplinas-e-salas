"""Root URL configuration."""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('academico/', include('academico.urls', namespace='academico')),
    path('pessoas/', include('pessoas.urls', namespace='pessoas')),
    path('infraestrutura/', include('infraestrutura.urls', namespace='infraestrutura')),
    path('alocacao/', include('alocacao.urls', namespace='alocacao')),
    path('relatorios/', include('relatorios.urls', namespace='relatorios')),
    path('api/', include('api.urls')), # api rest (viewsets ja existiam mas n tavam conectadas)
    path('api-auth/', include('rest_framework.urls')), # Autenticação paa fazer buscas na API
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger-ui/",SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui", ),
    path("api/schema/redoc/",SpectacularRedocView.as_view(url_name="schema"), name="redoc",),
]

