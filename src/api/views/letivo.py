from academico.models import PeriodoLetivo
from rest_framework import viewsets
from api.serializers.letivo import PeriodoLetivoSerializer
from rest_framework.permissions import IsAuthenticated

class PeriodoLetivoViewset(viewsets.ModelViewSet):
    queryset = PeriodoLetivo.objects.all()
    serializer_class = PeriodoLetivoSerializer
    permission_classes = [IsAuthenticated]
