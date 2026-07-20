from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from .models import RecursoSala, Sala


class RecursoSalaModelTest(TestCase):
    def test_str_mostra_nome(self):
        recurso = RecursoSala.objects.create(nome="projetor")

        self.assertEqual(str(recurso), "projetor")

    def test_nome_precisa_ser_unico(self):
        RecursoSala.objects.create(nome="projetor")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                RecursoSala.objects.create(nome="projetor")


class SalaModelTest(TestCase):
    def test_str_mostra_nome_e_capacidade(self):
        sala = Sala.objects.create(nome="sala 101", capacidade_alunos=40)

        self.assertEqual(str(sala), "sala 101 (40 alunos)")

    def test_nome_precisa_ser_unico(self):
        Sala.objects.create(nome="sala 101", capacidade_alunos=40)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Sala.objects.create(nome="sala 101", capacidade_alunos=20)

    def test_capacidade_minima_e_validada_no_full_clean(self):
        sala = Sala(nome="sala vazia", capacidade_alunos=0)

        with self.assertRaises(ValidationError):
            sala.full_clean()

    def test_sala_pode_ter_varios_recursos(self):
        projetor = RecursoSala.objects.create(nome="projetor")
        ar_condicionado = RecursoSala.objects.create(nome="ar-condicionado")
        sala = Sala.objects.create(nome="sala 101", capacidade_alunos=40)

        sala.recursos.add(projetor, ar_condicionado)

        self.assertEqual(sala.recursos.count(), 2)
        self.assertIn(sala, projetor.salas.all())

    def test_tipo_sala_padrao_e_comum(self):
        sala = Sala.objects.create(nome="sala 101", capacidade_alunos=40)

        self.assertEqual(sala.tipo_sala, Sala.TipoSala.COMUM)


class SalaListViewTest(TestCase):
    def test_view_carrega_sem_erro(self):
        response = self.client.get(reverse("infraestrutura:sala_list"))

        self.assertEqual(response.status_code, 200)
