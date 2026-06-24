from dataclasses import fields
from rest_framework import serializers
from alocacao.models import Horario

class HorarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Horario
        fields = '__all__'