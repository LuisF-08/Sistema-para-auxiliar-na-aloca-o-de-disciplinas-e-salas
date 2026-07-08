from academico.models import Disciplina
from rest_framework import viewsets
from api.serializers.diciplina import DiciplinaSerializer
from rest_framework.permissions import IsAuthenticated

class DisciplinaViewset(viewsets.ModelViewSet):
    queryset = Disciplina.objects.all()
    serializer_class = DiciplinaSerializer
    permission_classes = [IsAuthenticated]