from django.urls import path
from . import views

app_name = "relatorios"

urlpatterns = [
    path("professores/", views.RelatorioProfessoresView.as_view(), name="professores"),
    path("salas/", views.RelatorioSalasView.as_view(), name="salas"),
    path("grade/", views.RelatorioGradeView.as_view(), name="grade"),
    path("exportar/csv/", views.exportar_csv, name="exportar_csv"),
    path("exportar/pdf/", views.exportar_pdf, name="exportar_pdf"),
]
