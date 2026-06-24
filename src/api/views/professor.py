from rest_framework import viewsets
from pessoas.models import Professor
from api.serializers.professor import ProfessorSerializer
from rest_framework.permissions import IsAuthenticated

class ProfessorViewSet(viewsets.ModelViewSet):
    queryset = Professor.objects.all()
    serializer_class = ProfessorSerializer
    permission_classes = [IsAuthenticated]