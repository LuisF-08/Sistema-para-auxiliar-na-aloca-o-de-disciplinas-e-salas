from rest_framework import viewsets
from alocacao.models import Alocacao
from api.serializers.alocacao import AlocacaoSerializer
from rest_framework.permissions import IsAuthenticated

class AlocacaoViewSet(viewsets.ModelViewSet):
    queryset = Alocacao.objects.all()
    serializer_class = AlocacaoSerializer
    permission_classes = [IsAuthenticated]