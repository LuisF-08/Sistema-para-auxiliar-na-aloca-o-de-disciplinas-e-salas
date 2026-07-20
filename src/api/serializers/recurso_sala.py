from infraestrutura.models import RecursoSala
from rest_framework import serializers

class RecursoSalaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecursoSala
        fields = "__all__"