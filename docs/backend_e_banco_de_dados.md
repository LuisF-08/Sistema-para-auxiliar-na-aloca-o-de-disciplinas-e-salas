# Documentação — Backend e Banco de Dados

Sistema para auxiliar na alocação de disciplinas e salas.
Django 5.2 · PostgreSQL 17 · Python 3.14

---

## Sumário

1. [Visão geral do projeto](#1-visão-geral-do-projeto)
2. [Estrutura de pastas](#2-estrutura-de-pastas)
3. [Configurações principais](#3-configurações-principais)
4. [Banco de dados — configuração e conexão](#4-banco-de-dados--configuração-e-conexão)
5. [Models e entidades](#5-models-e-entidades)
6. [Relacionamentos entre entidades](#6-relacionamentos-entre-entidades)
7. [Constraints e índices no banco](#7-constraints-e-índices-no-banco)
8. [Regras de negócio](#8-regras-de-negócio)
9. [Camada de repositórios](#9-camada-de-repositórios)
10. [Camada de serviços](#10-camada-de-serviços)
11. [Admin Django](#11-admin-django)
12. [Migrations](#12-migrations)
13. [Testes automatizados](#13-testes-automatizados)
14. [API REST (estrutura futura)](#14-api-rest-estrutura-futura)
15. [Fluxo geral de uma alocação](#15-fluxo-geral-de-uma-alocação)
16. [Pontos de atenção e melhorias sugeridas](#16-pontos-de-atenção-e-melhorias-sugeridas)
17. [Alterações realizadas nesta sessão](#17-alterações-realizadas-nesta-sessão)
18. [Próximos passos recomendados](#18-próximos-passos-recomendados)
19. [Revisão geral, ambiente e testes (branch feature/testes-e-correcoes-ambiente)](#19-revisão-geral-ambiente-e-testes-branch-featuretestes-e-correcoes-ambiente)

---

## 1. Visão geral do projeto

O sistema resolve o problema de **alocar turmas em salas e professores em horários** sem que ocorram conflitos de sobreposição. Cada alocação registra: em qual período letivo, qual professor ministra, qual disciplina, para qual turma, em qual sala e em qual horário da semana.

O backend é construído em **Django 5.2** seguindo uma arquitetura orientada a domínio com cinco apps, separados por responsabilidade. O banco de dados é **PostgreSQL 17**, escolhido principalmente por suportar índices únicos parciais — o mecanismo que impede dois horários iguais no banco de forma atômica.

---

## 2. Estrutura de pastas

```
projeto/
├── .env                          ← variáveis sensíveis (não versionar)
├── .gitignore
├── manage.py
├── requirements.txt              ← dependências Python
├── docs/
│   └── backend_e_banco_de_dados.md  ← este arquivo
└── src/
    ├── config/                   ← configurações globais
    │   ├── settings.py
    │   ├── urls.py
    │   ├── wsgi.py
    │   └── asgi.py
    ├── academico/                ← cursos, períodos letivos, disciplinas
    │   ├── models.py
    │   ├── admin.py
    │   └── migrations/
    ├── alocacao/                 ← horários e alocações (núcleo do sistema)
    │   ├── models.py
    │   ├── admin.py
    │   ├── repositories/         ← consultas ao banco
    │   │   ├── alocacoes.py
    │   │   ├── horarios.py
    │   │   ├── professores.py
    │   │   └── salas.py
    │   ├── services/             ← lógica de negócio e operações
    │   │   ├── alocacoes.py
    │   │   └── conflitos.py
    │   ├── tests/
    │   │   └── tests.py
    │   └── migrations/
    ├── infraestrutura/           ← salas e recursos físicos
    │   ├── models.py
    │   ├── admin.py
    │   └── migrations/
    ├── pessoas/                  ← professores, turmas, disponibilidade
    │   ├── models.py
    │   ├── admin.py
    │   └── migrations/
    ├── relatorios/               ← dashboard, relatorios e exportacao (csv/pdf)
    └── api/                      ← api rest (dj rest framework), conectada em config/urls.py
        ├── views/
        └── serializers/
```

### Por que essa divisão em apps?

Cada app representa um **domínio de negócio** independente:

| App | Responsabilidade |
|---|---|
| `academico` | O currículo: o que existe (cursos, períodos, disciplinas) |
| `infraestrutura` | O espaço físico: o que está disponível (salas e recursos) |
| `pessoas` | Os atores humanos: quem ensina e quem aprende |
| `alocacao` | A operação central: juntar tudo num horário válido |
| `relatorios` | dashboard e relatorios (ocupação, professores, grade, export csv/pdf) |
| `api` | interface REST (viewsets do DRF, ver seção 14) |

> nota: essa tabela e o diagrama acima tavam desatualizados — diziam "não implementado" pra `relatorios` e `api`, mas os dois já tem bastante código funcionando. corrigido na sessão da seção 19.

---

## 3. Configurações principais

O arquivo de configurações fica em `src/config/settings.py`. Ele não contém nenhuma senha ou chave em texto — tudo é lido do arquivo `.env` via `python-decouple`.

```python
# leitura do .env
SECRET_KEY    = config("SECRET_KEY")
DEBUG         = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())
```

**Internacionalização:**

```python
LANGUAGE_CODE = "pt-br"
TIME_ZONE     = "America/Sao_Paulo"
USE_TZ        = True
```

`USE_TZ = True` faz o Django armazenar todos os datetimes em UTC no banco e converter para `America/Sao_Paulo` apenas na exibição. Isso evita bugs de horário de verão.

**Chave primária padrão:**

```python
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
```

Todas as PKs são `bigint` (64 bits), garantindo capacidade suficiente mesmo em tabelas com muitos registros.

---

## 4. Banco de dados — configuração e conexão

### Por que PostgreSQL 17?

O SQLite (banco padrão do Django) **não suporta** índices únicos parciais (`UniqueConstraint` com `condition=`). Esses índices são o mecanismo que impede, por exemplo, duas aulas confirmadas na mesma sala ao mesmo tempo — de forma atômica, sem race condition. Sem PostgreSQL, essa garantia simplesmente não existe no banco.

### Configuração no `settings.py`

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="alocacao_db"),
        "USER": config("DB_USER", default="postgres"),
        "PASSWORD": config("DB_PASSWORD", default=""),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
        "OPTIONS": {
            "connect_timeout": 10,
        },
    }
}
```

### Arquivo `.env` (desenvolvimento)

```
SECRET_KEY=django-insecure-...
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=alocacao_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

> **Atenção:** o `.env` já está no `.gitignore`. Nunca commite esse arquivo.
> Em produção, gere uma nova `SECRET_KEY` com:
> ```
> python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
> ```

### Driver de conexão

O driver usado é `psycopg[binary]>=3.1.0` (psycopg3). Essa é a versão mais recente e compatível com Django 5.2. O sufixo `[binary]` instala binários pré-compilados, eliminando a necessidade de compilador C na máquina.

### Como conectar ao banco pela primeira vez

```bash
# 1. criar o banco (no terminal com psql disponível)
createdb alocacao_db

# 2. ajustar o .env com usuário e senha corretos

# 3. aplicar todas as migrations
python manage.py migrate

# 4. criar usuário administrador
python manage.py createsuperuser
```

---

## 5. Models e entidades

### 5.1 `academico.TimeStampedModel` (abstract)

Base reutilizável que adiciona campos de auditoria em qualquer model que a herde:

```python
class TimeStampedModel(models.Model):
    criado_em    = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True
```

Os models `Curso`, `PeriodoLetivo` e `Disciplina` herdam desta classe. Os demais apps definem os campos de auditoria diretamente (inconsistência documentada na seção 16).

---

### 5.2 App `academico`

#### `Curso`

Representa um curso de graduação ou técnico.

| Campo | Tipo | Detalhe |
|---|---|---|
| `id` | bigint PK | auto-gerado |
| `nome` | varchar(120) | único |
| `codigo` | varchar(20) | único (ex: "CC", "ADS") |
| `ativo` | boolean | soft-delete |
| `criado_em` | timestamptz | auto |
| `atualizado_em` | timestamptz | auto |

---

#### `PeriodoLetivo`

Representa um semestre acadêmico (ex: 2025.1, 2026.2).

| Campo | Tipo | Detalhe |
|---|---|---|
| `id` | bigint PK | auto-gerado |
| `ano` | smallint | mínimo 2000 |
| `semestre` | smallint | apenas 1 ou 2 |
| `data_inicio` | date | — |
| `data_fim` | date | deve ser após `data_inicio` |
| `ativo` | boolean | indica período vigente |

**Constraints:**
- `periodo_letivo_semestre_valido`: semestre só pode ser 1 ou 2
- `periodo_letivo_datas_validas`: `data_fim > data_inicio`
- `periodo_letivo_unico`: combinação `(ano, semestre)` única

---

#### `Disciplina`

Uma matéria pertencente a um curso.

| Campo | Tipo | Detalhe |
|---|---|---|
| `id` | bigint PK | — |
| `curso` | FK → Curso | PROTECT |
| `nome` | varchar(120) | único por curso |
| `codigo` | varchar(30) | único por curso |
| `carga_horaria_semanal` | smallint | mínimo 1 hora |
| `periodo_recomendado` | smallint | nullable |
| `recursos_necessarios` | M2M → RecursoSala | ex: projetor, ar-condicionado |
| `ativo` | boolean | soft-delete |

O campo `recursos_necessarios` é fundamental para validar se uma sala candidata possui os equipamentos que a disciplina exige.

---

### 5.3 App `infraestrutura`

#### `RecursoSala`

Equipamento ou característica de uma sala (ex: projetor, ar-condicionado, computadores).

| Campo | Tipo | Detalhe |
|---|---|---|
| `id` | bigint PK | — |
| `nome` | varchar(80) | único |
| `descricao` | text | opcional |

---

#### `Sala`

Espaço físico onde as aulas acontecem.

| Campo | Tipo | Detalhe |
|---|---|---|
| `id` | bigint PK | — |
| `nome` | varchar(80) | único |
| `tipo_sala` | varchar(20) | `comum`, `laboratorio`, `auditorio`, `online` |
| `capacidade_alunos` | smallint | mínimo 1 |
| `localizacao` | varchar(120) | ex: "Bloco B, 2º andar" |
| `recursos` | M2M → RecursoSala | equipamentos disponíveis |
| `ativo` | boolean | soft-delete |

**Índices:**
- `sala_tipo_idx` em `tipo_sala`
- `sala_capacidade_idx` em `capacidade_alunos`

---

### 5.4 App `pessoas`

#### `Professor`

| Campo | Tipo | Detalhe |
|---|---|---|
| `id` | bigint PK | — |
| `nome` | varchar(120) | — |
| `email` | varchar | único, nullable |
| `especialidade` | varchar(120) | opcional |
| `carga_horaria_maxima` | smallint | limite de horas/semana |
| `ativo` | boolean | soft-delete |

O campo `carga_horaria_maxima` é consultado durante a validação de uma nova alocação para garantir que o professor não ultrapasse seu limite no período.

---

#### `Turma`

Grupo de alunos de um curso em um período específico.

| Campo | Tipo | Detalhe |
|---|---|---|
| `id` | bigint PK | — |
| `curso` | FK → Curso | PROTECT |
| `periodo_letivo` | FK → PeriodoLetivo | PROTECT |
| `nome` | varchar(80) | ex: "T1", "Noturno A" |
| `turno` | varchar(20) | `matutino`, `vespertino`, `noturno`, `integral` |
| `numero_alunos` | smallint | mínimo 1 |
| `ativo` | boolean | soft-delete |

**Constraint:** `turma_unica_por_periodo` — combinação `(curso, periodo_letivo, nome)` única.

---

#### `DisponibilidadeProfessor`

Registra explicitamente quando um professor está **indisponível** em um horário específico.

| Campo | Tipo | Detalhe |
|---|---|---|
| `id` | bigint PK | — |
| `professor` | FK → Professor | CASCADE |
| `horario` | FK → Horario | CASCADE |
| `disponivel` | boolean | `False` = bloqueado |
| `observacao` | varchar(160) | motivo do bloqueio |

**Constraint:** `disponibilidade_unica_por_professor_horario` — um professor só pode ter um registro de disponibilidade por horário.

> A exclusão em CASCADE significa que, ao deletar um professor ou um horário, todos os registros de disponibilidade associados são removidos automaticamente.

---

### 5.5 App `alocacao`

#### `Horario`

Define uma faixa de tempo recorrente na semana (ex: toda segunda das 08:00 às 10:00).

| Campo | Tipo | Detalhe |
|---|---|---|
| `id` | bigint PK | — |
| `dia_semana` | smallint | 1=segunda, 6=sábado |
| `horario_inicio` | time | — |
| `horario_fim` | time | deve ser após `horario_inicio` |
| `ativo` | boolean | soft-delete |

**Constraints:**
- `horario_faixa_unica`: `(dia_semana, horario_inicio, horario_fim)` único
- `horario_fim_maior_inicio`: check no banco, garante `horario_fim > horario_inicio`

---

#### `Alocacao` — entidade central

Une todos os outros elementos. É aqui que a grade horária é construída.

| Campo | Tipo | Detalhe |
|---|---|---|
| `id` | bigint PK | — |
| `periodo_letivo` | FK → PeriodoLetivo | PROTECT |
| `professor` | FK → Professor | PROTECT |
| `disciplina` | FK → Disciplina | PROTECT |
| `turma` | FK → Turma | PROTECT |
| `sala` | FK → Sala | PROTECT |
| `horario` | FK → Horario | PROTECT |
| `status` | varchar(20) | `planejada`, `confirmada`, `cancelada` |
| `observacao` | text | campo livre, opcional |

Todos os FKs usam `on_delete=PROTECT`, impedindo a exclusão de qualquer entidade referenciada enquanto houver alocações apontando para ela.

**Status possíveis:**
- `planejada` — criada, mas não confirmada; já ocupa o horário
- `confirmada` — confirmada oficialmente; ocupa o horário
- `cancelada` — liberada; não ocupa mais o horário

---

## 6. Relacionamentos entre entidades

```
Curso ──< Disciplina >── RecursoSala
  │                           │
  └──< Turma                  └──< Sala
         │
         └── FK: periodo_letivo

PeriodoLetivo ──< Turma
PeriodoLetivo ──< Alocacao

Professor ──< DisponibilidadeProfessor >── Horario

Alocacao ──FK── PeriodoLetivo
Alocacao ──FK── Professor
Alocacao ──FK── Disciplina
Alocacao ──FK── Turma
Alocacao ──FK── Sala
Alocacao ──FK── Horario
```

| Relacionamento | Tipo | Descrição |
|---|---|---|
| Curso → Disciplina | 1:N | um curso tem várias disciplinas |
| Curso → Turma | 1:N | um curso tem várias turmas |
| PeriodoLetivo → Turma | 1:N | um período tem várias turmas |
| PeriodoLetivo → Alocacao | 1:N | um período tem várias alocações |
| Professor → Alocacao | 1:N | um professor tem várias alocações |
| Turma → Alocacao | 1:N | uma turma tem várias alocações |
| Sala → Alocacao | 1:N | uma sala recebe várias alocações |
| Horario → Alocacao | 1:N | um horário é usado em várias alocações |
| Sala ↔ RecursoSala | M:N | uma sala tem vários recursos |
| Disciplina ↔ RecursoSala | M:N | uma disciplina exige vários recursos |
| Professor ↔ Horario (via DisponibilidadeProfessor) | M:N | registro de disponibilidade |

---

## 7. Constraints e índices no banco

### Por que isso importa?

Constraints no banco são a **última linha de defesa**. Mesmo que o código Python tenha um bug, o banco recusa qualquer dado inválido. Isso é especialmente importante em sistemas multiusuário, onde duas requisições simultâneas podem passar pela validação Python ao mesmo tempo.

### Índices únicos parciais — o coração da prevenção de conflitos

Esses três índices só aplicam a unicidade para alocações `planejada` ou `confirmada`. Alocações canceladas ficam de fora, permitindo que um horário seja reusado após cancelamento.

```sql
-- sala não pode ter duas aulas ativas no mesmo período/horário
CREATE UNIQUE INDEX aloc_sala_horario_sem_conflito
  ON alocacao_alocacao (periodo_letivo_id, sala_id, horario_id)
  WHERE status IN ('planejada', 'confirmada');

-- professor não pode ter duas aulas ativas no mesmo período/horário
CREATE UNIQUE INDEX aloc_prof_horario_sem_conflito
  ON alocacao_alocacao (periodo_letivo_id, professor_id, horario_id)
  WHERE status IN ('planejada', 'confirmada');

-- turma não pode ter duas aulas ativas no mesmo período/horário
CREATE UNIQUE INDEX aloc_turma_horario_sem_conflito
  ON alocacao_alocacao (periodo_letivo_id, turma_id, horario_id)
  WHERE status IN ('planejada', 'confirmada');
```

> Esses índices **só funcionam no PostgreSQL**. É a razão principal pela qual o SQLite foi abandonado.

### Outros constraints por tabela

| Tabela | Constraint | Descrição |
|---|---|---|
| `academico_periodoletivo` | `periodo_letivo_semestre_valido` | semestre deve ser 1 ou 2 |
| `academico_periodoletivo` | `periodo_letivo_datas_validas` | data_fim > data_inicio |
| `academico_periodoletivo` | `periodo_letivo_unico` | (ano, semestre) únicos |
| `academico_disciplina` | `disciplina_codigo_unico_por_curso` | código único por curso |
| `academico_disciplina` | `disciplina_nome_unico_por_curso` | nome único por curso |
| `pessoas_turma` | `turma_unica_por_periodo` | (curso, período, nome) únicos |
| `pessoas_disponibilidadeprofessor` | `disponibilidade_unica_por_professor_horario` | um registro por professor/horário |
| `alocacao_horario` | `horario_faixa_unica` | (dia, início, fim) únicos |
| `alocacao_horario` | `horario_fim_maior_inicio` | fim > início |

### Índices de performance

| Índice | Campos | Motivo |
|---|---|---|
| `periodo_letivo_idx` | (ano, semestre) | busca frequente por período |
| `disciplina_codigo_idx` | codigo | busca por código |
| `professor_nome_idx` | nome | busca por nome |
| `turma_periodo_idx` | periodo_letivo | filtro por período |
| `turma_curso_periodo_idx` | (curso, periodo_letivo) | filtro combinado |
| `sala_tipo_idx` | tipo_sala | filtro por tipo |
| `sala_capacidade_idx` | capacidade_alunos | filtro por lotação |
| `horario_dia_inicio_idx` | (dia_semana, horario_inicio) | listagem e busca |
| `aloc_periodo_status_idx` | (periodo_letivo, status) | filtro mais comum |
| `aloc_sala_horario_idx` | (periodo_letivo, sala, horario) | detecção de conflito |
| `aloc_prof_horario_idx` | (periodo_letivo, professor, horario) | detecção de conflito |
| `aloc_turma_horario_idx` | (periodo_letivo, turma, horario) | detecção de conflito |

---

## 8. Regras de negócio

As regras de negócio são validadas em dois lugares complementares:

1. **`Alocacao.clean()`** — validação em Python, com mensagens de erro amigáveis
2. **Constraints do banco** — validação atômica no PostgreSQL, segunda linha de defesa

O método `Alocacao.save()` é sobrescrito para sempre chamar `full_clean()`, garantindo que as regras sejam verificadas em **qualquer** operação de escrita, independente de quem chamou o `save()`.

```python
def save(self, *args, **kwargs):
    self.full_clean()  # executa clean() antes de qualquer save
    super().save(*args, **kwargs)
```

### As 8 regras implementadas em `Alocacao.clean()`

| # | Regra | Verificação |
|---|---|---|
| 1 | Período da alocação coerente com a turma | `alocacao.periodo_letivo == turma.periodo_letivo` |
| 2 | Capacidade da sala | `turma.numero_alunos <= sala.capacidade_alunos` |
| 3 | Conflito de sala | sala sem aula ativa no mesmo período/horário |
| 4 | Conflito de professor | professor sem aula ativa no mesmo período/horário |
| 5 | Conflito de turma | turma sem aula ativa no mesmo período/horário |
| 6 | Disponibilidade do professor | `DisponibilidadeProfessor.disponivel != False` |
| 7 | Recursos da sala | sala possui todos os recursos exigidos pela disciplina |
| 8 | Carga horária do professor | soma das cargas no período não ultrapassa `carga_horaria_maxima` |

**Importante — edição sem falso positivo:** ao editar uma alocação existente, as queries de conflito excluem a própria linha usando `qs.exclude(pk=self.pk)`, evitando que a alocação entre em conflito consigo mesma.

**Importante — import circular:** `DisponibilidadeProfessor` é importado dentro do método `clean()`, não no nível do módulo. Isso evita importação circular: `pessoas.models` faz referência a `alocacao.Horario`, e importar `pessoas.models` no topo de `alocacao.models` criaria um ciclo.

### Como os erros são retornados

```python
erros = {
    "sala":      ["a sala já possui uma aula ativa neste horário e período."],
    "professor": ["o professor está marcado como indisponível neste horário."],
}
raise ValidationError(erros)
```

O Django Admin e o service `mapear_conflitos()` interpretam esse formato, exibindo cada mensagem ao lado do campo correto no formulário.

---

## 9. Camada de repositórios

Centralizam as consultas ao banco em `src/alocacao/repositories/`. Nenhum código fora dessa camada deve escrever queries complexas diretamente.

### `repositories/alocacoes.py`

| Função | O que faz |
|---|---|
| `alocacoes_ativas(periodo_letivo=None)` | QuerySet de alocações ativas com `select_related` para evitar N+1 |
| `carga_horaria_professor(professor, periodo_letivo)` | Soma a carga semanal do professor no período |
| `ocupacao_por_sala(periodo_letivo)` | Contagem de alocações por sala no período |

### `repositories/horarios.py`

| Função | O que faz |
|---|---|
| `horarios_livres_para_turma(turma)` | Horários em que a turma não tem aula |
| `horarios_livres_para_professor(professor, periodo_letivo)` | Horários em que o professor não tem aula |

### `repositories/professores.py`

| Função | O que faz |
|---|---|
| `professores_disponiveis(periodo_letivo, horario)` | Professores ativos, sem aula e sem bloqueio no horário |

### `repositories/salas.py`

| Função | O que faz |
|---|---|
| `salas_livres(periodo_letivo, horario, capacidade_minima, recursos)` | Salas ativas, livres no horário, com filtros opcionais |

---

## 10. Camada de serviços

Contém a lógica de negócio que envolve mudança de estado ou operações compostas.

### `services/alocacoes.py`

```python
criar_alocacao(*, periodo_letivo, professor, disciplina, turma, sala, horario,
               status="planejada", observacao="")
```
Monta o objeto, chama `full_clean()` explicitamente e salva. Retorna a alocação criada.

```python
confirmar_alocacao(alocacao)
```
Muda o status para `confirmada` e salva. O `save()` sobrescrito revalida.

```python
cancelar_alocacao(alocacao)
```
Muda o status para `cancelada`. Cancelamentos liberam o horário — os índices únicos parciais excluem o status `cancelada`.

### `services/conflitos.py`

Verifica conflitos **sem salvar** no banco. Útil para pré-validar candidatos antes de exibir ao usuário.

```python
mapear_conflitos(alocacao)   # retorna dict de erros, {} se ok
possui_conflito(alocacao)    # retorna True/False
validar_sem_conflito(alocacao)  # levanta ValidationError se houver conflito
```

---

## 11. Admin Django

Interface de usuário funcional disponível em `http://localhost:8000/admin/`.

### `AlocacaoAdmin`

- **`list_select_related`**: carrega todos os relacionamentos numa única query JOIN — sem N+1
- **`autocomplete_fields`**: todos os FKs usam autocomplete — sem dropdowns com centenas de itens
- **Ação `confirmar_alocacoes`**: muda status, captura `ValidationError` e exibe mensagem de erro por alocação
- **Ação `cancelar_alocacoes`**: muda status para `cancelada`

---

## 12. Migrations

### Estado atual

| App | Migrations | O que cria |
|---|---|---|
| `academico` | `0001_initial` | Curso, PeriodoLetivo, Disciplina + constraints + índices |
| `infraestrutura` | `0001_initial` | RecursoSala, Sala + tabela M2M + índices |
| `pessoas` | `0001_initial` | Professor, Turma, DisponibilidadeProfessor + constraints + índices |
| `alocacao` | `0001_initial` + `0002_initial` | Horario, Alocacao + todos os constraints + índices parciais |

O app `alocacao` tem duas migrations porque `Alocacao` tem FKs para apps diferentes. A segunda migration resolve as dependências entre apps.

### Comandos essenciais

```bash
# aplicar em ambiente novo
python manage.py migrate

# verificar se há pendências
python manage.py migrate --check

# verificar se os models estão sincronizados
python manage.py makemigrations --check --dry-run

# criar nova migration após editar models
python manage.py makemigrations
python manage.py migrate
```

> Nunca edite arquivos de migration manualmente sem entender bem o que está fazendo.

---

## 13. Testes automatizados

```bash
# rodar tudo, app por app (necessario por causa do layout de pastas, ver aviso abaixo)
python manage.py test academico infraestrutura pessoas alocacao relatorios

# rodar so um app
python manage.py test alocacao

# com detalhes
python manage.py test alocacao --verbosity=2
```

> Os testes precisam de PostgreSQL ativo — o Django cria e destrói um banco de testes temporário.

> **atenção — `python manage.py test` sem argumento acha 0 testes.** o codigo do projeto mora em `src/`, mas `src/` n é um pacote python (n tem `__init__.py` e nunca teve a intenção de ser importado como `src.alocacao`, etc). o `manage.py` so funciona pq insere `src/` direto no `sys.path`. só que a descoberta automatica de testes do Django (`DiscoverRunner`), quando não recebe nenhum app_label, varre a partir do diretório onde o `manage.py` roda (a raiz do repo) — e lá não tem nenhum teste, só o `src/`. por isso sempre roda passando os apps explicitamente (`python manage.py test academico infraestrutura pessoas alocacao relatorios`), é assim que ta documentado acima. isso foi encontrado e confirmado na sessão da seção 19; não fizemos a mudança estrutural (mover `manage.py` pra dentro de `src/`, por ex.) pq é mais invasivo do que o escopo pedido — fica registrado como sugestão pra próxima sessão.

### Cobertura dos testes

| App | O que é testado |
|---|---|
| `alocacao` | alocação válida salva; conflito de sala, professor, turma; capacidade; disponibilidade; recursos; carga horária; período; status; services (`criar_alocacao`, `cancelar_alocacao`); repositories; `mapear_conflitos` |
| `academico` | unicidade de `Curso` (nome/código); constraints de `PeriodoLetivo` (semestre 1/2, datas, unicidade ano+semestre); unicidade de `Disciplina` por curso; view `disciplina_list` |
| `infraestrutura` | unicidade de `RecursoSala`/`Sala`; capacidade mínima; relação m2m sala↔recurso; view `sala_list` |
| `pessoas` | unicidade de e-mail do `Professor`; constraint `turma_unica_por_periodo`; constraint de `DisponibilidadeProfessor`; cascade ao apagar professor; views de listagem/criação de professor (inclui teste de regressão do bug corrigido, ver seção 19) |
| `relatorios` | funções de cálculo (`calcular_taxa_ocupacao`, `calcular_eficiencia_espaco`, `calcular_horarios_pico`, `detectar_conflitos_ativos`); views de dashboard/relatórios/grade; exportação csv e pdf |

> nota sobre `detectar_conflitos_ativos`: essa função busca duplicatas de sala/horário e professor/horário nas alocações ativas, mas os índices únicos parciais do banco (seção 7) já impedem que essas duplicatas existam de verdade — então na prática ela sempre vai retornar `0` conflitos enquanto os índices tiverem no lugar. o teste cobre só o caminho feliz por isso; é mais uma rede de segurança (caso os índices sejam removidos um dia) do que um cenário alcançável hoje.

---

## 14. API REST

A API REST (Django REST Framework) já tinha as views, serializers e o router prontos em `src/api/`, mas nunca tinha sido conectada no `urls.py` principal — corrigido na sessão da seção 19.

```
api/
├── urls.py              ← router do DRF com professores, horarios, alocacoes, salas
├── serializers/
│   ├── alocacao.py
│   ├── horario.py
│   ├── professor.py
│   └── sala.py
└── views/
    ├── alocacao.py
    ├── horario.py
    ├── professor.py
    └── sala.py
```

Endpoints disponíveis (todos exigem usuário autenticado, via `IsAuthenticated` + `DEFAULT_PERMISSION_CLASSES`):

- `/api/professores/`
- `/api/horarios/`
- `/api/alocacoes/`
- `/api/salas/`

A arquitetura em camadas facilita a implementação — as views da API apenas chamam os services, que chamam os repositórios:

```python
# exemplo de como ficaria uma view de criação
class AlocacaoCreateView(APIView):
    def post(self, request):
        serializer = AlocacaoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        alocacao = criar_alocacao(**serializer.validated_data)
        return Response(AlocacaoSerializer(alocacao).data, status=201)
```

---

## 15. Fluxo geral de uma alocação

```
Usuário (Admin ou API futura)
    │
    ▼
Service: criar_alocacao(periodo, professor, disciplina, turma, sala, horario)
    │
    ├── instancia Alocacao(...)
    │
    ▼
Alocacao.full_clean()  →  Alocacao.clean()
    │
    ├── Regra 1: período da alocação == período da turma?
    ├── Regra 2: numero_alunos <= capacidade_alunos?
    ├── Regra 3: sala já tem aula ativa neste horário?
    ├── Regra 4: professor já tem aula ativa neste horário?
    ├── Regra 5: turma já tem aula ativa neste horário?
    ├── Regra 6: professor está marcado indisponível?
    ├── Regra 7: sala tem todos os recursos da disciplina?
    └── Regra 8: professor ultrapassa carga horária máxima?
         │
         ├── [ERRO] → lança ValidationError com mensagens por campo
         │
         └── [OK] ↓
                  │
    ▼
Alocacao.save()
    │
    ├── full_clean() (chamado novamente — save() sobrescrito garante isso)
    │
    └── INSERT no PostgreSQL
          │
          ├── Índices únicos parciais verificados atomicamente
          │   ├── aloc_sala_horario_sem_conflito
          │   ├── aloc_prof_horario_sem_conflito
          │   └── aloc_turma_horario_sem_conflito
          │
          ├── [ERRO] → IntegrityError (race condition detectada pelo banco)
          │
          └── [OK] → alocacao salva, retornada ao chamador
```

### Por que validar duas vezes?

- A validação em Python (`clean()`) oferece **mensagens amigáveis** em português
- A validação no banco (`UniqueConstraint`) é a **garantia final** contra race conditions em acessos simultâneos

---

## 16. Pontos de atenção e melhorias sugeridas

### `TimeStampedModel` centralizado

`TimeStampedModel` está definido em `academico/models.py`, mas `Professor`, `Sala`, `Horario` e outros declaram `criado_em`/`atualizado_em` manualmente. Duplicação desnecessária.

**Melhoria:** mover para `src/core/models.py` e fazer todos os models herdar de lá.

---

### Soft-delete sem manager customizado

Os models usam `ativo = BooleanField(default=True)`, mas não há um `Manager` que filtre por `ativo=True` automaticamente. Toda query precisa adicionar `.filter(ativo=True)` manualmente.

**Melhoria:** criar um `ActiveManager` como manager padrão, com `objects_all` para acesso sem filtro.

---

### Sem `select_for_update()` nos serviços

Em ambientes com múltiplos usuários simultâneos, duas requisições podem passar pela validação Python ao mesmo tempo. Os índices únicos no banco barram isso, mas a mensagem retornada seria uma `IntegrityError` genérica, não um `ValidationError` amigável.

**Melhoria:** adicionar `select_for_update()` nas queries dentro de `clean()` para garantir mensagem amigável mesmo em concorrência.

---

### ~~App `relatorios` não implementado~~ — resolvido

Já tem dashboard, relatório de professores, de salas, de grade e exportação csv/pdf (ver seção 2). Só faltava cobertura de teste, que foi adicionada na seção 19.

---

### ~~API REST não implementada~~ — resolvido (parcialmente)

As views/serializers/router do DRF já existiam, só n tavam conectadas no `urls.py` principal — conectado na sessão da seção 19. Ainda falta: autenticação além de session/basic auth (token ou JWT, pra fazer sentido um app mobile/frontend externo consumir), paginação nos endpoints, e testes automatizados da api em si (só testamos que ela exige autenticação e que o router responde).

---

### Testes precisam de PostgreSQL

Os testes usam banco real. Correto para integração, mas torna o ambiente mais complexo.

**Sugestão:** criar `settings_test.py` com SQLite para testes unitários rápidos, mantendo PostgreSQL apenas para testes que precisam validar os constraints parciais.

---

## 17. Alterações realizadas nesta sessão

Esta seção documenta todas as mudanças feitas em relação ao estado original do projeto após o rebase.

### `requirements.txt` — atualizado

**Antes:**
```
Django==5.2.14
```

**Depois:**
```
Django==5.2.14
psycopg[binary]>=3.1.0
python-decouple>=3.8
```

**Por quê:** o SQLite não suporta `UniqueConstraint` com `condition=`. O psycopg3 é o driver oficial para PostgreSQL 17 com Django 5.2. O python-decouple isola credenciais do código.

---

### `src/config/settings.py` — reescrito

**Mudanças:**
- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` movidos para `.env` via `python-decouple`
- Banco alterado de SQLite para PostgreSQL 17
- Credenciais lidas do `.env`
- `connect_timeout: 10` adicionado
- `STATICFILES_DIRS` adicionado
- Comentários em português/minúsculo

---

### `.env` — criado

Arquivo criado na raiz do projeto com variáveis de ambiente para desenvolvimento local. Já está no `.gitignore`.

---

### `src/alocacao/repositories/salas.py` — corrigido

**Problema:** após o refactor que separou os models em apps distintos, o arquivo continuou importando de locais errados.

```python
# antes (errado)
from alocacao.models import Sala
from alocacao.selectors.alocacoes import alocacoes_ativas

# depois (correto)
from infraestrutura.models import Sala
from alocacao.repositories.alocacoes import alocacoes_ativas
```

---

### `src/alocacao/repositories/professores.py` — corrigido

```python
# antes (errado)
from alocacao.models import DisponibilidadeProfessor, Professor
from alocacao.selectors.alocacoes import alocacoes_ativas

# depois (correto)
from pessoas.models import DisponibilidadeProfessor, Professor
from alocacao.repositories.alocacoes import alocacoes_ativas
```

---

### `src/alocacao/repositories/horarios.py` — corrigido

```python
# antes (errado)
from alocacao.selectors.alocacoes import alocacoes_ativas

# depois (correto)
from alocacao.repositories.alocacoes import alocacoes_ativas
```

---

### `src/alocacao/tests/tests.py` — corrigido

**Problema:** todos os imports eram relativos (`from .models import ...`), mas o ponto `.` aponta para `alocacao.tests`, que não tem models. Além disso, importavam de `selectors` (diretório que nunca existiu — o correto é `repositories`).

```python
# antes (errado — imports relativos inválidos)
from .models import (Alocacao, Curso, Disciplina, ...)
from .selectors.alocacoes import carga_horaria_professor, ocupacao_por_sala
from .selectors.horarios import horarios_livres_para_turma
from .selectors.salas import salas_livres
from .services.alocacoes import cancelar_alocacao, criar_alocacao
from .services.conflitos import mapear_conflitos

# depois (correto — imports absolutos para os apps certos)
from alocacao.models import Alocacao, Horario
from academico.models import Curso, Disciplina, PeriodoLetivo
from infraestrutura.models import RecursoSala, Sala
from pessoas.models import DisponibilidadeProfessor, Professor, Turma
from alocacao.repositories.alocacoes import carga_horaria_professor, ocupacao_por_sala
from alocacao.repositories.horarios import horarios_livres_para_turma
from alocacao.repositories.salas import salas_livres
from alocacao.services.alocacoes import cancelar_alocacao, criar_alocacao
from alocacao.services.conflitos import mapear_conflitos
```

---

### `src/alocacao/models.py` — expandido

**Adicionado `__str__` em `Alocacao`:**
```python
def __str__(self):
    return f"alocacao #{self.pk or 'nova'} [{self.status}]"
```

**Adicionado `clean()` com 8 regras de negócio:**
As regras eram testadas mas nunca enforced no model. Qualquer `save()` direto via ORM, admin action ou script bypasava todas as validações.

**Adicionado `save()` override:**
```python
def save(self, *args, **kwargs):
    self.full_clean()
    super().save(*args, **kwargs)
```

Garante que `clean()` seja sempre executado, independente de quem chamou o `save()`.

---

### Dependências instaladas

```
psycopg==3.3.4
psycopg-binary==3.3.4
python-decouple==3.8
```

### Comandos executados e resultados

| Comando | Resultado |
|---|---|
| `pip install -r requirements.txt` | sucesso |
| `python manage.py check` | `System check identified no issues (0 silenced)` |
| `python manage.py makemigrations --check --dry-run` | `No changes detected` |
| Verificação de imports | `todos os imports carregados com sucesso` |
| Verificação de `Alocacao.clean` | `True` |
| Verificação de `save override` | `True` |

---

## 18. Próximos passos recomendados

### Para conectar ao PostgreSQL 17

```bash
# criar o banco
createdb alocacao_db

# ajustar .env com suas credenciais locais

# aplicar migrations
python manage.py migrate

# criar superusuário
python manage.py createsuperuser
```

### Para rodar os testes (precisa de PostgreSQL ativo)

```bash
python manage.py test alocacao --verbosity=2
```

### Para produção

1. Gerar nova `SECRET_KEY`:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
2. Definir `DEBUG=False` no `.env`
3. Definir `ALLOWED_HOSTS` com o domínio real
4. Usar senha forte no banco
5. Configurar um servidor WSGI (Gunicorn) e proxy reverso (Nginx)

### Próximas implementações sugeridas

1. **Manager de soft-delete** — evitar `.filter(ativo=True)` espalhado por todo o código
2. **`TimeStampedModel` centralizado** — mover para `src/core/models.py`
3. **Autenticação da API** — hoje é só session/basic auth do DRF; avaliar token ou JWT se algum client externo (mobile, frontend separado) for consumir
4. **Testes automatizados da própria API REST** — os testes atuais cobrem os apps de domínio, mas não os endpoints do DRF em si (serializers, viewsets, permissões por método)
5. **Comando `seed_alocacao`** — citado em `docs/modelo-dados.md` mas nunca foi implementado; ou implementa ou tira a referência (ver seção 19)

Ver seção 19 pra tudo que já foi revisado, corrigido e testado nessa sessão.

---

## 19. Revisão geral, ambiente e testes (branch `feature/testes-e-correcoes-ambiente`)

Essa seção documenta a revisão completa do projeto feita antes de começar a codar qualquer coisa nova: análise do projeto inteiro, conferência das dependências, montagem do ambiente local, e depois os bugs achados e corrigidos + testes adicionados. O foco de banco de dados dessa sessão ficou por conta da revisão manual (models, constraints, migrations já eram sólidos e n precisaram de mudança); o resto (ambiente, bugs, testes, docs) foi tocado nessa branch.

### Ambiente — o que foi configurado na máquina

- venv criado em `.venv/` com Python 3.14.3
- dependências do `requirements.txt` instaladas + as duas que faltavam nele (ver abaixo)
- PostgreSQL 17 rodando via Docker (`docker run --name alocacao_postgres -e POSTGRES_DB=alocacao_db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:17`) — Docker Desktop já tava instalado, só precisou ser iniciado
- `.env` local criado (não vai pro git) com `SECRET_KEY` gerada e as credenciais do container acima
- `migrate` rodado com sucesso contra o Postgres real — os índices únicos parciais da seção 7 foram confirmados funcionando no banco de verdade, não só na migration

### `requirements.txt` — dependências que faltavam

O arquivo listava só `Django`, `psycopg[binary]`, `python-decouple` e `reportlab`, mas o código já importava (e precisava de) mais duas coisas que nunca foram adicionadas:

```python
# src/config/settings.py
from dotenv import load_dotenv   # precisa de python-dotenv

# INSTALLED_APPS
'rest_framework',                 # precisa de djangorestframework
```

Um `pip install -r requirements.txt` limpo (ambiente novo, sem nada instalado antes) quebrava na hora de subir o servidor. Adicionado `djangorestframework>=3.15` e `python-dotenv>=1.0` no arquivo.

### `.env.example` — criado

Não existia nenhum, apesar do `.gitignore` já prever `.env.example`/`.env.sample` como exceção. Criado na raiz com todas as variáveis que `settings.py` exige (`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`) e comentários de como gerar a secret key.

### Bugs encontrados e corrigidos

Todos esses foram achados rodando o projeto de verdade (check, migrate, suite de testes) e não só lendo o código — por isso a suite de testes cresceu junto com a correção, cada bug ganhou um teste de regressão.

| # | Arquivo | Bug | Sintoma |
|---|---|---|---|
| 1 | `src/alocacao/tests/` | faltava `__init__.py` | `python manage.py test` (ou `test alocacao`) achava **0 testes**, mesmo com 19 testes prontos e passando. o diretório não era reconhecido como pacote python. |
| 2 | `src/pessoas/views.py` | `professor_list` chamava `render(...)` sem importar `render` de `django.shortcuts` | `NameError` — a página de listagem de professores quebrava sempre que alguém acessava `/pessoas/professores/` |
| 3 | `src/pessoas/views.py` e `src/academico/views.py` | `success_url = reverse_lazy('professor_create')` / `reverse_lazy('turma_create')` sem o namespace do app | `NoReverseMatch` — criar, editar ou excluir um professor/turma salvava certinho no banco, mas quebrava na hora do redirect de sucesso. corrigido pra `reverse_lazy('pessoas:professor_create')` e `reverse_lazy('academico:turma_create')` |
| 4 | `src/api/serializers/*.py` (4 arquivos) | `from dataclasses import fields` — import morto, sobrou de algum copia-e-cola, não tem nada a ver com DRF | nenhum erro (import válido, só não usado), mas é lixo no código — removido |
| 5 | `src/config/urls.py` | rotas da api (`src/api/urls.py`, router do DRF já pronto com professores/horarios/alocacoes/salas) nunca foram incluídas | api inteira ficava inacessível (404 em qualquer `/api/...`), apesar do código todo já existir. adicionado `path('api/', include('api.urls'))` |

O bug #3 é o mais sério dos achados: ele só aparece depois que o formulário é validado e salvo com sucesso, então testes manuais rápidos ("abri a tela, o formulário existe") não pegam — só apareceu rodando um teste de POST de verdade.

### Testes adicionados

Antes só o app `alocacao` tinha teste de verdade (19 testes); `academico`, `infraestrutura`, `pessoas` e `relatorios` tinham só o stub padrão do django (`# Create your tests here.`). Total agora: **66 testes**, todos passando contra o Postgres real.

| App | Testes | Cobre |
|---|---|---|
| `academico` | 11 | constraints de `Curso`, `PeriodoLetivo`, `Disciplina`; view de listagem |
| `infraestrutura` | 7 | constraints de `RecursoSala`, `Sala`; relação m2m com recursos; view de listagem |
| `pessoas` | 12 | constraints de `Professor`, `Turma`, `DisponibilidadeProfessor`; cascade; views (regressão dos bugs #2 e #3) |
| `relatorios` | 17 | funções de cálculo do dashboard; todas as views; exportação csv/pdf |
| `alocacao` | 19 | já existia, sem mudança de conteúdo (só ganhou o `__init__.py` do bug #1) |

```bash
# como rodar tudo (precisa do postgres ativo, ver seção 4)
python manage.py test academico infraestrutura pessoas alocacao relatorios --verbosity=2
```

### Observações que não viraram mudança de código (fora do escopo dessa sessão)

- **`python manage.py test` sem app_label acha 0 testes** — é do jeito que o `src/` foi estruturado (não é pacote python, só entra no `sys.path` via `manage.py`). daria pra resolver movendo o `manage.py` pra dentro de `src/` ou configurando um `pytest.ini`/`pyproject.toml` com `rootdir`, mas é uma mudança estrutural maior do que o pedido — documentado na seção 13 e aqui como sugestão.
- **`detectar_conflitos_ativos` (relatorios/views.py) nunca acha conflito de verdade** — os índices únicos parciais (seção 7) impedem que uma sala/professor tenha duas alocações ativas no mesmo horário, então a checagem de duplicata dessa função é inalcançável enquanto os índices existirem. não é bug, só uma observação (documentado na seção 13).
- **`docs/modelo-dados.md` cita um comando `seed_alocacao`** que não existe no código — não criamos o comando (não foi pedido), só deixamos registrado que a doc tá na frente do código nesse ponto.
- **`load_dotenv()` + `python-decouple` juntos em `settings.py`** — meio redundante (o decouple já lê o `.env` sozinho), mas funciona e não foi mexido pra não ficar fazendo mudança sem necessidade.

### Resultado final da sessão

| Comando | Resultado |
|---|---|
| `python manage.py check` | `System check identified no issues (0 silenced)` |
| `python manage.py makemigrations --check --dry-run` | `No changes detected` |
| `python manage.py migrate` (contra Postgres 17 real, via Docker) | todas as migrations aplicadas sem erro |
| `python manage.py test academico infraestrutura pessoas alocacao relatorios` | **66 testes, todos passando** |
