from infraestrutura.models import RecursoSala
from rest_framework import viewsets
from api.serializers.recurso_sala import RecursoSalaSerializer
from rest_framework.permissions import IsAuthenticated

class RecursoSalaViewset(viewsets.ModelViewSet):
    queryset = RecursoSala.objects.all()
    serializer_class = RecursoSalaSerializer
    permission_classes = [IsAuthenticated]