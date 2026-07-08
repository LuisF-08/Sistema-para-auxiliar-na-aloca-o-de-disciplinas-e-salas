# modelo de dados

este documento descreve a base de dados do sistema de alocacao de disciplinas e salas.

## banco usado agora

o ambiente (dev e producao) usa postgresql 17, tanto local quanto em producao. esse texto aqui dizia sqlite antes, mas isso ficou desatualizado desde a migracao documentada em `docs/backend_e_banco_de_dados.md` (secao 4 e 17) — o sqlite n suporta os indices unicos parciais (`UniqueConstraint` com `condition=`) que o app `alocacao` usa pra travar conflito de horario, entao o projeto trocou pra postgresql.

pra rodar localmente, o jeito mais rapido e um container docker (ver secao 19 de `docs/backend_e_banco_de_dados.md`). as credenciais ficam no `.env` (nunca vai pro git — usa o `.env.example` como base).

## entidades principais

### curso

representa o curso academico. exemplo: sistemas de informacao.

campos principais:

- `nome`
- `codigo`
- `ativo`

### periodo letivo

representa o recorte de ano/semestre onde a grade acontece.

campos principais:

- `ano`
- `semestre`
- `data_inicio`
- `data_fim`
- `ativo`

regras:

- cada par `ano + semestre` deve ser unico
- semestre deve ser 1 ou 2
- data final precisa ser maior que data inicial

### professor

representa o docente e seu limite semanal.

campos principais:

- `nome`
- `email`
- `especialidade`
- `carga_horaria_maxima`
- `ativo`

### disciplina

representa a disciplina ofertada por um curso.

campos principais:

- `curso`
- `nome`
- `codigo`
- `carga_horaria_semanal`
- `periodo_recomendado`
- `recursos_necessarios`
- `ativo`

regras:

- o codigo da disciplina e unico por curso
- o nome da disciplina e unico por curso

### turma

representa um grupo de alunos dentro de curso e periodo letivo.

campos principais:

- `curso`
- `periodo_letivo`
- `nome`
- `turno`
- `numero_alunos`
- `ativo`

regras:

- turma e unica por `curso + periodo_letivo + nome`

### sala

representa ambiente fisico ou online usado em aula.

campos principais:

- `nome`
- `tipo_sala`
- `capacidade_alunos`
- `localizacao`
- `recursos`
- `ativo`

### horario

representa uma faixa semanal de aula.

campos principais:

- `dia_semana`
- `horario_inicio`
- `horario_fim`
- `ativo`

regras:

- a faixa `dia + inicio + fim` e unica
- horario final precisa ser maior que horario inicial

### disponibilidade do professor

representa se o professor esta disponivel ou indisponivel em um horario.

campos principais:

- `professor`
- `horario`
- `disponivel`
- `observacao`

regras:

- cada professor tem no maximo um registro por horario

### alocacao

liga periodo, professor, disciplina, turma, sala e horario.

campos principais:

- `periodo_letivo`
- `professor`
- `disciplina`
- `turma`
- `sala`
- `horario`
- `status`
- `observacao`

status:

- `planejada`
- `confirmada`
- `cancelada`

regras:

- sala n pode ter duas alocacoes ativas no mesmo periodo e horario
- professor n pode ter duas alocacoes ativas no mesmo periodo e horario
- turma n pode ter duas alocacoes ativas no mesmo periodo e horario
- turma n pode passar da capacidade da sala
- professor indisponivel n pode ser alocado
- sala precisa ter os recursos exigidos pela disciplina
- carga semanal do professor n pode passar do limite cadastrado
- periodo da alocacao precisa ser o mesmo periodo da turma
- alocacao cancelada n conta como conflito

## services

os services ficam em `src/alocacao/services/`.

eles executam regras de negocio e operacoes:

- `criar_alocacao`
- `confirmar_alocacao`
- `cancelar_alocacao`
- `mapear_conflitos`
- `possui_conflito`
- `validar_sem_conflito`

## selectors

os selectors ficam em `src/alocacao/selectors/`.

eles concentram consultas reutilizaveis:

- alocacoes ativas
- carga horaria do professor
- ocupacao por sala
- horarios livres da turma
- horarios livres do professor
- professores disponiveis
- salas livres

## seed

> **atenção:** esse comando ainda n existe no codigo (n tem `management/commands/` em nenhum app). fica registrado aqui como proposta, n como algo que já funciona. quem for implementar, o objetivo e esse:

para criar dados simulados:

```powershell
.venv\Scripts\python manage.py seed_alocacao
```

a ideia e o comando ser idempotente: rodar mais de uma vez sem duplicar a base principal.
