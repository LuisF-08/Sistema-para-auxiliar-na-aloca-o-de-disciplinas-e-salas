from rest_framework import viewsets
from infraestrutura.models import Sala
from api.serializers.sala import SalaSerializer
from rest_framework.permissions import IsAuthenticated

class SalaViewSet(viewsets.ModelViewSet):
    queryset = Sala.objects.all()
    serializer_class = SalaSerializer
    permission_classes = [IsAuthenticated]