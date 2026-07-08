from rest_framework import viewsets
from pessoas.models import Turma
from api.serializers.turma import TurmaSerializer
from rest_framework.permissions import IsAuthenticated

class TurmaViewset(viewsets.ModelViewSet):
    queryset = Turma.objects.all()
    serializer_class = TurmaSerializer
    permission_classes = [IsAuthenticated]