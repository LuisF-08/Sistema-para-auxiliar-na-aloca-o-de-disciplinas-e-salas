"""Root URL configuration."""
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api-aloca/", include("rest_framework.urls"))
]
