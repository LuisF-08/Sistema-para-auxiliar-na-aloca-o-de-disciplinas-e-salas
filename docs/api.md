# Documentação da API - Sistema de Alocação de Disciplinas e Salas

## Objetivo

A API foi desenvolvida utilizando **Django REST Framework (DRF)** e tem como objetivo disponibilizar os dados do sistema para integração entre frontend, backend e futuras aplicações externas.

---

# Arquitetura

```text
Cliente
    ↓
ViewSet (DRF)
    ↓
Service
    ↓
Repository
    ↓
Model
    ↓
PostgreSQL
```

| Camada | Responsabilidade |
|---------|------------------|
| ViewSet | Receber requisições HTTP e retornar respostas JSON |
| Service | Aplicar regras de negócio |
| Repository | Consultar e manipular dados |
| Model | Representar as entidades do banco |
| PostgreSQL | Persistência dos dados |

---

# Autenticação

A API utiliza autenticação do **Django REST Framework**.

Antes de consumir qualquer endpoint protegido é necessário realizar o **login** para obter um **token de acesso**.

Fluxo:

```text
Login
   ↓
Recebe Token
   ↓
Authorization: Bearer <token>
   ↓
Consome a API
```

ou

Use o Superusuário para acessar a **API** para obter o acesso com **superuser**.

```bash
python manage.py createsuperuser   # crie super ususario e use suas credenciais para consumo da api
```

Fluxo:

```text
Login via admin
   ↓
coloca credenciais Nome e Senha
   ↓
   ↓
Consome a API
```

Caso o token não seja enviado ou esteja inválido, a API retornará:

```http
401 Unauthorized
```

---

# Estrutura

```
api/
├── serializers/
├── views/
├── services/
├── repositories/
├── permissions.py
└── urls.py
```

---

# Rotas

As rotas são registradas através do **DefaultRouter** do Django REST Framework.

```python
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r'professores', ProfessorViewSet)
router.register(r'horarios', HorarioViewSet)
router.register(r'alocacoes', AlocacaoViewSet)
router.register(r'salas', SalaViewSet)
router.register(r'curso', CursoViewset)
router.register(r'disciplina', DisciplinaViewset)
router.register(r'disponibilidade-professor', DisponibilidadeProfessorViewset)
router.register(r'periodo-letivo', PeriodoLetivoViewset)
router.register(r'recurso-sala', RecursoSalaViewset)
router.register(r'turma', TurmaViewset)

urlpatterns = router.urls
```

---

# Endpoints

Todos os recursos seguem o padrão REST do DRF.

## Professores

| Método | Endpoint |
|---------|----------|
| GET | `/api/professores/` |
| POST | `/api/professores/` |
| GET | `/api/professores/{id}/` |
| PUT | `/api/professores/{id}/` |
| PATCH | `/api/professores/{id}/` |
| DELETE | `/api/professores/{id}/` |

---

## Salas

| Método | Endpoint |
|---------|----------|
| GET | `/api/salas/` |
| POST | `/api/salas/` |
| GET | `/api/salas/{id}/` |
| PUT | `/api/salas/{id}/` |
| PATCH | `/api/salas/{id}/` |
| DELETE | `/api/salas/{id}/` |

---

## Horários

| Método | Endpoint |
|---------|----------|
| GET | `/api/horarios/` |
| POST | `/api/horarios/` |
| GET | `/api/horarios/{id}/` |
| PUT | `/api/horarios/{id}/` |
| PATCH | `/api/horarios/{id}/` |
| DELETE | `/api/horarios/{id}/` |

---

## Alocações

| Método | Endpoint |
|---------|----------|
| GET | `/api/alocacoes/` |
| POST | `/api/alocacoes/` |
| GET | `/api/alocacoes/{id}/` |
| PUT | `/api/alocacoes/{id}/` |
| PATCH | `/api/alocacoes/{id}/` |
| DELETE | `/api/alocacoes/{id}/` |

---

## Cursos

| Método | Endpoint |
|---------|----------|
| GET | `/api/curso/` |
| POST | `/api/curso/` |
| GET | `/api/curso/{id}/` |
| PUT | `/api/curso/{id}/` |
| PATCH | `/api/curso/{id}/` |
| DELETE | `/api/curso/{id}/` |

---

## Disciplinas

| Método | Endpoint |
|---------|----------|
| GET | `/api/disciplina/` |
| POST | `/api/disciplina/` |
| GET | `/api/disciplina/{id}/` |
| PUT | `/api/disciplina/{id}/` |
| PATCH | `/api/disciplina/{id}/` |
| DELETE | `/api/disciplina/{id}/` |

---

## Turmas

| Método | Endpoint |
|---------|----------|
| GET | `/api/turma/` |
| POST | `/api/turma/` |
| GET | `/api/turma/{id}/` |
| PUT | `/api/turma/{id}/` |
| PATCH | `/api/turma/{id}/` |
| DELETE | `/api/turma/{id}/` |

---

## Períodos Letivos

| Método | Endpoint |
|---------|----------|
| GET | `/api/periodo-letivo/` |
| POST | `/api/periodo-letivo/` |
| GET | `/api/periodo-letivo/{id}/` |
| PUT | `/api/periodo-letivo/{id}/` |
| PATCH | `/api/periodo-letivo/{id}/` |
| DELETE | `/api/periodo-letivo/{id}/` |

---

## Disponibilidade dos Professores

| Método | Endpoint |
|---------|----------|
| GET | `/api/disponibilidade-professor/` |
| POST | `/api/disponibilidade-professor/` |
| GET | `/api/disponibilidade-professor/{id}/` |
| PUT | `/api/disponibilidade-professor/{id}/` |
| PATCH | `/api/disponibilidade-professor/{id}/` |
| DELETE | `/api/disponibilidade-professor/{id}/` |

---

## Recursos das Salas

| Método | Endpoint |
|---------|----------|
| GET | `/api/recurso-sala/` |
| POST | `/api/recurso-sala/` |
| GET | `/api/recurso-sala/{id}/` |
| PUT | `/api/recurso-sala/{id}/` |
| PATCH | `/api/recurso-sala/{id}/` |
| DELETE | `/api/recurso-sala/{id}/` |

---

# Exemplo de Requisição

```http
POST /api/professores/
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{
    "nome": "João Silva",
    "email": "joao@email.com"
}
```

---

# Exemplo de Resposta

```json
{
    "id": 1,
    "nome": "João Silva",
    "email": "joao@email.com"
}
```

---

# Documentação Automática

A API utiliza o **drf-spectacular** para geração automática da documentação OpenAPI.

Instalação:

```bash
pip install drf-spectacular
```

Documentação disponível em:

```
/api/schema/   -> baixa em formato .yaml a documentação
/api/schema/swagger-ui/
```

---

# Tecnologias

- Python 3
- Django
- Django REST Framework (DRF)
- PostgreSQL
- drf-spectacular

---

# Observações

- Todos os endpoints retornam dados em formato JSON.
- Os ViewSets são registrados automaticamente pelo `DefaultRouter`.
- Para acessar endpoints protegidos é obrigatório realizar autenticação e enviar o token de acesso.
- A documentação Swagger é gerada automaticamente pelo DRF através do drf-spectacular.