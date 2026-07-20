from academico.models import PeriodoLetivo
from rest_framework import serializers

class PeriodoLetivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodoLetivo
        fields = "__all__"