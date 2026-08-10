"""Root URL configuration."""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

admin.site.site_header = "SADAS — Administração"
admin.site.site_title = "SADAS Admin"
admin.site.index_title = "Painel de Alocação Acadêmica"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='alocacao:dashboard'), name='root'),
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

