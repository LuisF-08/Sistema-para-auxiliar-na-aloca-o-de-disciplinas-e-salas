# Documentação Inicial da API - Sistema de Alocação de Disciplinas e Salas

## Objetivo

A API tem como objetivo disponibilizar os dados do sistema para integração entre frontend, backend, dashboards e futuras aplicações externas.

A API seguirá o padrão REST utilizando Django REST Framework (DRF).

---

# Arquitetura

```text
Request
   ↓
APIView
   ↓
Service
   ↓
Repository
   ↓
Model
   ↓
PostgreSQL
```

### Responsabilidades

| Camada     | Responsabilidade                     |
| ---------- | ------------------------------------ |
| APIView    | Receber e responder requisições HTTP |
| Service    | Aplicar regras de negócio            |
| Repository | Consultar e manipular dados          |
| Model      | Representar entidades do banco       |
| PostgreSQL | Persistência dos dados               |

---

# Estrutura da API

```text
api/
├── serializers/
│   ├── professor.py
│   ├── sala.py
│   ├── horario.py
│   └── alocacao.py
│
├── views/
│   ├── professor.py
│   ├── sala.py
│   ├── horario.py
│   └── alocacao.py
│
├── urls.py
└── permissions.py
```

---

## Função de Cada Pasta

### serializers/

Responsável por converter objetos Python/Django em JSON e JSON em objetos Python.

Exemplo:

- Recebe um objeto `Professor`.
- Converte para JSON na resposta da API.
- Valida dados recebidos em requisições POST e PUT.

---

### views/

Responsável por receber as requisições HTTP da API.

Funções:

- Processar requisições GET, POST, PUT e DELETE.
- Chamar os Services para executar regras de negócio.
- Retornar respostas em JSON.

---

### urls.py

Centraliza o mapeamento dos endpoints da API.

Exemplo:

```python
path("professores/", ProfessorListAPIView.as_view())
```

---

# Endpoints

## Professores

### Listar Professores

```http
GET /api/professores/
```

### Buscar Professor

```http
GET /api/professores/{id}/
```

### Cadastrar Professor

```http
POST /api/professores/
```

### Atualizar Professor

```http
PUT /api/professores/{id}/
```

### Remover Professor

```http
DELETE /api/professores/{id}/
```

### Exemplo de Resposta

```json
{
  "id": 1,
  "nome": "João Silva",
  "email": "joao@universidade.br"
}
```

---

## Salas

### Listar Salas

```http
GET /api/salas/
```

### Buscar Sala

```http
GET /api/salas/{id}/
```

### Cadastrar Sala

```http
POST /api/salas/
```

### Atualizar Sala

```http
PUT /api/salas/{id}/
```

### Remover Sala

```http
DELETE /api/salas/{id}/
```

### Exemplo de Resposta

```json
{
  "id": 1,
  "nome": "Laboratório 01",
  "capacidade": 40
}
```

---

## Horários

### Listar Horários

```http
GET /api/horarios/
```

### Buscar Horário

```http
GET /api/horarios/{id}/
```

### Cadastrar Horário

```http
POST /api/horarios/
```

### Atualizar Horário

```http
PUT /api/horarios/{id}/
```

### Remover Horário

```http
DELETE /api/horarios/{id}/
```

---

## Alocações

### Listar Alocações

```http
GET /api/alocacoes/
```

### Buscar Alocação

```http
GET /api/alocacoes/{id}/
```

### Criar Alocação

```http
POST /api/alocacoes/
```

### Remover Alocação

```http
DELETE /api/alocacoes/{id}/
```

### Exemplo de Requisição

```json
{
  "professor": 1,
  "sala": 5,
  "horario": 3,
  "disciplina": 2
}
```

### Exemplo de Resposta

```json
{
  "id": 10,
  "professor": 1,
  "sala": 5,
  "horario": 3,
  "disciplina": 2
}
```

---

# Endpoints de Negócio

## Verificar Conflitos de Alocação

Permite identificar conflitos de horários, salas ou professores.

### Endpoint

```http
GET /api/alocacoes/conflitos/
```

### Exemplo de Resposta

```json
{
  "conflitos": [
    {
      "professor": "João Silva",
      "problema": "Professor alocado em dois horários simultâneos"
    }
  ]
}
```

### Regras Validadas

* Professor não pode estar em dois horários simultaneamente.
* Sala não pode possuir duas disciplinas no mesmo horário.
* Disciplina não pode possuir alocações duplicadas.

---

# Dashboard

Fornece dados estatísticos para exibição nos painéis administrativos.

### Endpoint

```http
GET /api/dashboard/
```

### Exemplo de Resposta

```json
{
  "total_professores": 50,
  "total_salas": 20,
  "total_disciplinas": 80,
  "total_alocacoes": 180,
  "conflitos": 4
}
```

---

# Fluxo de Desenvolvimento

## Repository

Responsável pelas consultas ao banco.

Exemplo:

```python
def listar_salas_disponiveis():
    return Sala.objects.filter(ativa=True)
```

---

## Services

Responsáveis pelas regras de negócio.

Exemplo:

```python
def criar_alocacao(dados):
    validar_conflitos(dados)

    return Alocacao.objects.create(**dados)
```

---

## API Views

Responsáveis por receber requisições HTTP.

Exemplo:

```python
class SalaListAPIView(APIView):

    def get(self, request):
        salas = listar_salas_disponiveis()

        serializer = SalaSerializer(
            salas,
            many=True
        )

        return Response(serializer.data)
```

---

# Documentação Automática

A API deverá utilizar:

```bash
pip install djangorestframework
pip install drf-spectacular
```

Endpoints da documentação:

```http
/api/schema/
/api/schema/swagger-ui/
```

---

# Entregas Previstas da Sprint

* CRUD de Professores.
* CRUD de Salas.
* CRUD de Horários.
* CRUD de Alocações.
* Endpoint de Conflitos.
* Endpoint de Dashboard.
* Integração com PostgreSQL 17.
* Documentação automática da API.
* Integração com frontend do sistema.

---

# Resultado Esperado

Ao final da sprint, a API deverá permitir:

* Consulta e gerenciamento dos dados acadêmicos.
* Criação e manutenção das alocações.
* Identificação automática de conflitos.
* Alimentação dos dashboards administrativos.
* Integração entre frontend e backend.
* Base preparada para futuras aplicações móveis ou integrações externas.
