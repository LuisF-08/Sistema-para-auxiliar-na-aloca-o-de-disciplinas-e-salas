function abrirModalCriar() {
  const form = document.getElementById('formDisciplina');
  const modalTitle = document.getElementById('disciplinaModalLabel');
  const submitBtn = form.querySelector('button[type="submit"]');

  modalTitle.textContent = 'Nova Disciplina';
  submitBtn.textContent = 'Criar registro';
  form.action = form.dataset.createUrl || '';
  form.reset();
}

function abrirModalEditar(botao) {
  const form = document.getElementById('formDisciplina');
  const modalTitle = document.getElementById('disciplinaModalLabel');
  const submitBtn = form.querySelector('button[type="submit"]');

  modalTitle.textContent = 'Editar Disciplina';
  submitBtn.textContent = 'Salvar alterações';
  form.action = botao.getAttribute('data-url');

  document.getElementById('id_codigo').value = botao.getAttribute('data-codigo') || '';
  document.getElementById('id_nome').value = botao.getAttribute('data-nome') || '';
  document.getElementById('id_curso').value = botao.getAttribute('data-curso') || '';
  document.getElementById('id_carga_horaria_semanal').value = botao.getAttribute('data-carga') || '';
  document.getElementById('id_periodo').value = botao.getAttribute('data-periodo') || '';
}

function abrirModalExcluir(botao) {
  const form = document.getElementById('formExcluir');
  form.action = botao.getAttribute('data-url');
  document.getElementById('nomeExcluir').textContent = botao.getAttribute('data-nome') || '';
}
