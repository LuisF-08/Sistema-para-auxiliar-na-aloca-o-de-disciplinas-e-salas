from rest_framework import viewsets # <-- Adicionado o 's' no final
from pessoas.models import DisponibilidadeProfessor
from rest_framework.permissions import IsAuthenticated
from api.serializers.disponibilidade_professor import DisponibilidadeProfessorSerializer

# Alterado de ModelSerializer para ModelViewSet:
class DisponibilidadeProfessorViewset(viewsets.ModelViewSet): 
    queryset = DisponibilidadeProfessor.objects.all()
    serializer_class = DisponibilidadeProfessorSerializer
    permission_classes = [IsAuthenticated] # <-- Corrigido também de 'permissions_classes' para 'permission_classes' (no singular)