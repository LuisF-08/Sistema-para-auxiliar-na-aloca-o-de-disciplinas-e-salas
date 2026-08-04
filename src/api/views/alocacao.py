from rest_framework import viewsets
from alocacao.models import STATUS_ATIVOS_ALOCACAO, Alocacao
from api.serializers.alocacao import AlocacaoSerializer
from rest_framework.permissions import IsAuthenticated

DIAS_DISPLAY_PARA_CODIGO = {
    'Segunda-feira': '1',
    'Terça-feira': '2',
    'Quarta-feira': '3',
    'Quinta-feira': '4',
    'Sexta-feira': '5',
    'Sábado': '6',
}


class AlocacaoViewSet(viewsets.ModelViewSet):
    queryset = Alocacao.objects.all()
    serializer_class = AlocacaoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Alocacao.objects.filter(status__in=STATUS_ATIVOS_ALOCACAO)
        horario = self.request.query_params.get('horario')
        dia_semana = self.request.query_params.get('dia_semana')
        professor = self.request.query_params.get('professor')
        sala = self.request.query_params.get('sala')

        if horario:
            queryset = queryset.filter(horario_id=horario)
        if dia_semana:
            codigo = DIAS_DISPLAY_PARA_CODIGO.get(dia_semana, dia_semana)
            queryset = queryset.filter(horario__dia_semana=codigo)
        if professor:
            queryset = queryset.filter(professor_id=professor)
        if sala:
            queryset = queryset.filter(sala_id=sala)

        return queryset
