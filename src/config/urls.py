"""Root URL configuration."""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pessoas/', include('pessoas.urls')),
    path('academico/', include('academico.urls')),
    path('relatorios/', include('relatorios.urls')),
]