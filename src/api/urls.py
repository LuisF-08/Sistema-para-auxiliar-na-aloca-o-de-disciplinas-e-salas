from rest_framework.routers import DefaultRouter

from api.views.alocacao import AlocacaoViewSet
from api.views.horario import HorarioViewSet
from api.views.professor import ProfessorViewSet
from api.views.sala import SalaViewSet
from api.views.curso import CursoViewset
from api.views.disciplina import DisciplinaViewset
from api.views.disponibilidade_professor import DisponibilidadeProfessorViewset
from api.views.letivo import PeriodoLetivoViewset
from api.views.recurso_sala import RecursoSalaViewset
from api.views.turma import TurmaViewset

router = DefaultRouter()

router.register(r'professores', ProfessorViewSet)
router.register(r'horarios', HorarioViewSet)
router.register(r'alocacoes', AlocacaoViewSet)
router.register(r'salas', SalaViewSet)
router.register(r'curso',CursoViewset)
router.register(r'disciplina', DisciplinaViewset)
router.register(r'disponibilidade-professor',DisponibilidadeProfessorViewset)
router.register(r'periodo-letivo',PeriodoLetivoViewset)
router.register(r'recurso-sala', RecursoSalaViewset)
router.register(r'turma', TurmaViewset)


urlpatterns = router.urls