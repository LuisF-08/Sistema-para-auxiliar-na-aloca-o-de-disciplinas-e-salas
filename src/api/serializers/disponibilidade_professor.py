from pessoas.models import DisponibilidadeProfessor
from rest_framework import serializers

class DisponibilidadeProfessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisponibilidadeProfessor
        fields = "__all__"