# Desafio 2 — Sistema Web para Alocação de Disciplinas e Salas

## Objetivo

Desenvolver um sistema web utilizando Django para gerenciar a alocação de disciplinas, professores, turmas, salas e horários, evitando conflitos automaticamente e gerando relatórios.

---

## Tecnologias

- Backend: Django 5.x
- Frontend: Django Templates + Bootstrap 5
- Banco de Dados: PostgreSQL / SQLite
- Linguagem: Python 3.12+
- Gestão Ágil: Trello ou Jira

---

## Funcionalidades Principais

### Cadastro de:

- Professores
- Disciplinas
- Turmas
- Salas
- Horários

### Alocação

Permitir vincular:

- Professor
- Disciplina
- Turma
- Sala
- Horário

### Dashboard

- Indicadores de ocupação
- Estatísticas das salas
- Carga horária dos professores

### Relatórios

- PDF
- Excel

---

## Requisitos Funcionais

### RF1
Cadastrar, editar e excluir:
- Professores
- Disciplinas
- Turmas
- Salas
- Horários

### RF2
Criar alocações entre professor, disciplina, turma, sala e horário.

### RF3
Detectar conflitos automaticamente antes de salvar.

### RF4
Gerar relatórios de ocupação.

### RF5
Disponibilizar dashboard administrativo.

### RF6
Exportar relatórios em PDF e Excel.

---

## Requisitos Não Funcionais

- Verificação de conflitos em menos de 500 ms
- Autenticação obrigatória
- Adequação à LGPD
- Interface responsiva
- Compatibilidade com Docker
- Código seguindo PEP 8
- Cobertura mínima de 70% de testes

---

## Regras de Negócio

### RC1 — Conflito de Sala

Uma sala não pode possuir duas aulas no mesmo horário.

### RC2 — Conflito de Professor

Um professor não pode ministrar aulas simultaneamente.

### RC3 — Conflito de Turma

Uma turma não pode estar em duas aulas no mesmo horário.

### RC4 — Capacidade da Sala

A quantidade de alunos da turma não pode exceder a capacidade da sala.

### RC5 — Carga Horária

A carga horária semanal do professor não pode ultrapassar seu limite cadastrado.

---

## Modelo de Dados

### Entidades

- Professor
- Disciplina
- Turma
- Sala
- Horário
- Alocação

A entidade **Alocação** relaciona todas as demais entidades.

---

## Estrutura do Projeto

```text
desafio2/
│
├── manage.py
├── desafio2/
│   ├── settings.py
│   └── urls.py
│
├── alocacao/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   └── templates/
│
└── static/
```

## Interface

### Bootstrap 5

- Navbar
- Dashboard
- Formulários
- Tabelas responsivas

### Dashboard

Exibe:

- Total de salas
- Total de alocações
- Ocupação por sala
- Carga horária dos professores

---

## Relatórios

Implementação utilizando ReportLab para geração de:

- Grade horária em PDF
- Relatórios administrativos

---

## Testes

Testes unitários para:

- Conflito de sala
- Conflito de professor
- Conflito de turma
- Capacidade da sala

Meta:

- Cobertura mínima de 70%

---

## Cronograma

| Semana | Entrega |
|---------|----------|
| 1 | Reunião inicial |
| 2 | Levantamento de requisitos |
| 3 | Arquitetura |
| 4 | Protótipo |
| 5 | Banco de dados |
| 6 | Cadastro de professores e disciplinas |
| 7 | Cadastro de salas e turmas |
| 8 | Horários |
| 9 | Verificação de conflitos |
| 10 | Relatórios |
| 11 | Testes |
| 12 | Ajustes finais |
| 13 | Relatório final |

---

## MVP

- CRUD completo
- Alocações com validação
- Dashboard
- Relatórios PDF
- Testes automatizados
- Login administrativo
- Interface responsiva
- README
- Deploy funcional

---

## Evoluções Futuras

- Alocação automática com IA (OR-Tools)
- API REST com Django REST Framework
- Notificações de conflito
- Importação CSV
- Autenticação institucional (SSO)

---

## Resumo

O sistema tem como objetivo automatizar a alocação de disciplinas e salas em instituições de ensino, reduzindo conflitos de horários, controlando a utilização dos espaços físicos e fornecendo relatórios e indicadores para apoio à gestão acadêmica.