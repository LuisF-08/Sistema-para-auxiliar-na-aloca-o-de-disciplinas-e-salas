from rest_framework import viewsets
from alocacao.models import Alocacao
from api.serializers.alocacao import AlocacaoSerializer
from rest_framework.permissions import IsAuthenticated

class AlocacaoViewSet(viewsets.ModelViewSet):
    queryset = Alocacao.objects.all()
    serializer_class = AlocacaoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Alocacao.objects.all()
        horario = self.request.query_params.get('horario')

        if horario:
            queryset = queryset.filter(horario_id=horario)
            
        return queryset