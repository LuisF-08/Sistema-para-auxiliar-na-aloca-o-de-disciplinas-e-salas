"""Root URL configuration."""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
<<<<<<< HEAD
    path("api-aloca/", include("rest_framework.urls"))
]
=======
    path('pessoas/', include('pessoas.urls')),     # Conecta as rotas de professores
    path('academico/', include('academico.urls')), # Conecta as rotas de turmas
]
>>>>>>> d85d6f23949072640156e3b55be0b41a7ec1d569
