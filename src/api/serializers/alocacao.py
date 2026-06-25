from dataclasses import fields
from rest_framework import serializers
from alocacao.models import Alocacao


class AlocacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alocacao
        fields = '__all__'