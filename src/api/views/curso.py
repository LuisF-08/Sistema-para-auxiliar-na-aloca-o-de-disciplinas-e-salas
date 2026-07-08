from rest_framework import viewsets
from academico.models import Curso
from api.serializers.curso import CursoSerializer
from rest_framework.permissions import IsAuthenticated

class CursoViewset(viewsets.ModelViewSet):
    queryset = Curso.objects.all()
    serializer_class = CursoSerializer
    permission_classes = [IsAuthenticated]
    