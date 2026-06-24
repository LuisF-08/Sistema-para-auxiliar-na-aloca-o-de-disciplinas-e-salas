from rest_framework import viewsets
from alocacao.models import Horario
from api.serializers.horario import HorarioSerializer
from rest_framework.permissions import IsAuthenticated 

class HorarioViewSet(viewsets.ModelViewSet):
    queryset = Horario.objects.all()
    serializer_class = HorarioSerializer 
    permission_classes = [IsAuthenticated]