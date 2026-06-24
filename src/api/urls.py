from rest_framework.routers import DefaultRouter

from api.views.alocacao import AlocacaoViewSet
from api.views.horario import HorarioViewSet
from api.views.professor import ProfessorViewSet
from api.views.sala import SalaViewSet

router = DefaultRouter()

router.register(r'professores', ProfessorViewSet)
router.register(r'horarios', HorarioViewSet)
router.register(r'alocacoes', AlocacaoViewSet)
router.register(r'salas', SalaViewSet)

urlpatterns = router.urls