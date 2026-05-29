# Desenvolvimento de um Sistema para Auxiliar na Alocação de Disciplinas e Salas

## 🎯 Objetivo Geral
Desenvolver um sistema inteligente capaz de auxiliar na alocação eficiente de disciplinas e salas, considerando restrições acadêmicas, capacidade física, disponibilidade de professores e otimização do uso dos espaços.

## 🎯 Objetivos Específicos
1. Mapear as restrições acadêmicas e estruturais (horários, carga horária, capacidade das salas, recursos disponíveis).
2. Estruturar um banco de dados contendo:
   - Disciplinas
   - Professores
   - Turmas
   - Salas
   - Horários disponíveis
3. Desenvolver algoritmo de alocação considerando:
   - Capacidade da sala
   - Disponibilidade de professor
   - Conflitos de horário
   - Otimização do uso dos espaços
4. Implementar interface para visualização e edição das alocações.
5. Gerar relatórios de ocupação e conflitos.
6. Permitir simulações de cenários alternativos.
7. Documentar a solução e validar com dados reais ou simulados.

## 📌 Justificativa
A alocação manual de disciplinas e salas é um processo complexo, sujeito a conflitos, retrabalho e uso ineficiente dos espaços físicos. Muitas instituições ainda realizam esse planejamento por meio de planilhas, o que aumenta o risco de:
- Choque de horários
- Superlotação de salas
- Subutilização de ambientes
- Conflitos de disponibilidade docente

O desenvolvimento de um sistema automatizado contribui para:
- Melhor planejamento acadêmico
- Otimização da infraestrutura
- Redução de erros humanos
- Agilidade no processo de montagem de horários
- Transparência na tomada de decisão

## 📊 Dados Necessários
- Lista de disciplinas
- Carga horária
- Número de alunos por turma
- Capacidade das salas
- Disponibilidade de professores
- Grade curricular

## ⚠ Restrições e Limitações
- O sistema deve respeitar regras acadêmicas vigentes.
- Dados sensíveis devem ser protegidos.
- Pode haver limitações de integração com sistemas institucionais.
- O tempo de desenvolvimento pode limitar a implementação de algoritmos mais complexos.
- Preferência por ferramentas *open source*.

## 🌍 Impacto Esperado
- Redução de conflitos de horário
- Melhor aproveitamento das salas
- Processo mais transparente e ágil
- Base para expansão futura (ex: otimização por IA)
- Cultura institucional orientada por dados

## 🎯 Objetivos Funcionais do Sistema
O sistema deverá permitir:
- Cadastro de disciplinas
- Cadastro de professores
- Cadastro de turmas
- Cadastro de salas
- Controle de horários disponíveis
- Alocação automática ou semiautomática
- Identificação de conflitos
- Geração de grade horária
- Relatórios de ocupação
- Dashboard administrativo

## 📊 Funcionalidades Esperadas

### 🔹 Módulo Acadêmico
- Cadastro de cursos
- Cadastro de disciplinas
- Cadastro de professores
- Cadastro de turmas

### 🔹 Módulo de Infraestrutura
- Cadastro de salas
- Capacidade das salas
- Recursos disponíveis (projetor, laboratório etc.)

### 🔹 Módulo de Alocação
- Associação disciplina ↔ professor ↔ sala
- Verificação automática de conflitos
- Sugestão de horários

### 🔹 Dashboard
- Ocupação das salas
- Horários livres
- Indicadores de conflitos

### 🔹 Relatórios
- Grade horária
- Uso das salas
- Conflitos encontrados
- Relatórios exportáveis

## ✅ MVP Esperado
Ao final da Fase 2, o sistema deverá:
- Permitir cadastro acadêmico completo
- Identificar conflitos de horários
- Auxiliar na alocação de disciplinas e salas
- Gerar relatórios
- Disponibilizar dashboard funcional
- Possuir interface web operacional