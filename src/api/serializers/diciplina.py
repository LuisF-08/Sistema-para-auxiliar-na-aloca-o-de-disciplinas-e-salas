from academico.models import Disciplina
from rest_framework import serializers

class DiciplinaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disciplina
        fields = "__all__"
    