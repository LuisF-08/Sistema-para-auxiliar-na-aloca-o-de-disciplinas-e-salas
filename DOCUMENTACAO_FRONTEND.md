# Documentação Técnica: Frontend e Integração de Views (CRUD Dinâmico)

Esta documentação descreve o padrão de arquitetura adotado no desenvolvimento das interfaces do sistema (Turmas, Professores, Salas e Disciplinas), focando na experiência do usuário fluida (baseada em protótipos do Figma) e na integração com o backend Django.

## 1. Padrão Arquitetural: CRUD em Tela Única (Modais)

Para evitar recarregamentos de página desnecessários e manter a fidelidade visual com os protótipos do Figma, foi adotada uma estratégia de **CRUD Dinâmico em Tela Única** utilizando **HTML5/CSS3 (Bootstrap 5)**, **Django Views** e **JavaScript vanilla**.

### Fluxo de Funcionamento:
1. **Listagem (GET):** O Django renderiza a página contendo a tabela de registros e um único Modal de formulário (inicialmente oculto).
2. **Criação (POST):** Ao clicar em `+ Novo Registro`, o JavaScript limpa o formulário do modal e altera o atributo `action` do `<form>` para a URL de criação correspondente:
   * URL: `/academico/disciplinas/nova/`
3. **Edição (POST com ID):** Ao clicar no ícone de lápis em uma linha da tabela, os atributos `data-*` do botão populam os campos do modal instantaneamente via JavaScript. O `action` do formulário é alterado dinamicamente para a rota de atualização contendo a chave primária (`pk`) do registro:
   * URL: `/academico/disciplinas/<pk>/update/` (Exemplo: `/academico/disciplinas/5/update/`)
4. **Exclusão (POST/DELETE):** Feito de forma segura através de pequenos formulários em linha que disparam uma confirmação nativa (`confirm()`) antes de enviar a requisição para a View de remoção correspondente:
   * URL: `/academico/disciplinas/<pk>/delete/` (Exemplo: `/academico/disciplinas/5/delete/`)

---

## 2. Estrutura do Frontend (Templates)

Os templates herdam de uma base comum (`base.html`) para manter a consistência visual.

### Componentes Principais:
* **Header / Controle de Página:** Título principal, contador de registros dinâmico e o botão disparador do Modal.
* **Barra de Busca:** Campo estilizado para filtragem de registros em tempo de execução.
* **Tabela Responsiva:** Listagem limpa contendo as colunas de dados e a coluna de ações (Editar e Excluir).
* **Modal Unificado:** Formulário único com IDs bem definidos (`id="formDisciplina"`, `id_nome`, etc.) para permitir a manipulação via Javascript.

---

## 3. Lógica do JavaScript de Integração

O JavaScript no final de cada template serve como ponte entre o estado visual do HTML e as Views do Django.

```javascript
// 1. Escuta o clique de edição em todos os botões "lápis" da tabela
document.querySelectorAll('.btn-edit-disciplina').forEach(botao => {
    botao.addEventListener('click', function() {
        // Altera o título e os textos do modal para o contexto de Edição
        document.getElementById('disciplinaModalLabel').innerText = "Editar Disciplina";
        document.getElementById('btnSalvar').innerText = "Salvar alterações";

        // Coleta os dados embutidos na linha da tabela
        const id = this.getAttribute('data-id');
        document.getElementById('id_nome').value = this.getAttribute('data-nome');
        document.getElementById('id_codigo').value = this.getAttribute('data-codigo');
        document.getElementById('id_curso').value = this.getAttribute('data-curso');
        
        // Define dinamicamente o endpoint de envio para a View de Update
        document.getElementById('formDisciplina').action = `/academico/disciplinas/atualizar/${id}/`;
    });
});

// 2. Reseta o modal para o contexto de Criação ao clicar em "Novo Registro"
function prepararParaCriar() {
    document.getElementById('disciplinaModalLabel').innerText = "Nova Disciplina";
    document.getElementById('btnSalvar').innerText = "Criar registro";
    document.getElementById('formDisciplina').reset();
    document.getElementById('formDisciplina').action = "/academico/disciplinas/criar/";
}

## 4. Estrutura das Views (Django Python)

Seguindo o princípio de responsabilidade única, as Views foram divididas em funções individuais e isoladas dentro de cada módulo.

# Exemplo de arquitetura aplicada em academico/views.py

def disciplina_list(request):
    """Renderiza a listagem geral de dados."""
    ...

def disciplina_create(request):
    """Processa o recebimento de dados e insere um novo registro no banco."""
    ...

def disciplina_update(request, pk):
    """Busca o objeto pelo ID (pk) e atualiza seus campos no banco de dados."""
    ...

def disciplina_delete(request, pk):
    """Remove com segurança um registro específico."""
    ...