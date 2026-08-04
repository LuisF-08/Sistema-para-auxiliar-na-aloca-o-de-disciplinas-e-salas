function abrirModalCriar() {
  const form = document.getElementById('formTurma');
  const modalTitle = document.getElementById('turmaModalLabel');
  const submitBtn = form.querySelector('button[type="submit"]');

  modalTitle.textContent = 'Nova Turma';
  submitBtn.textContent = 'Criar registro';
  form.action = form.dataset.createUrl || '';
  form.reset();
}

function abrirModalEditar(botao) {
  const form = document.getElementById('formTurma');
  const modalTitle = document.getElementById('turmaModalLabel');
  const submitBtn = form.querySelector('button[type="submit"]');

  modalTitle.textContent = 'Editar Turma';
  submitBtn.textContent = 'Salvar alterações';
  form.action = botao.getAttribute('data-url');

  document.getElementById('id_nome').value = botao.getAttribute('data-nome') || '';
  document.getElementById('id_curso').value = botao.getAttribute('data-curso') || '';
  document.getElementById('id_periodo_letivo').value = botao.getAttribute('data-periodo') || '';
  document.getElementById('id_numero_alunos').value = botao.getAttribute('data-alunos') || '';
  document.getElementById('id_turno').value = botao.getAttribute('data-turno') || '';
}

function abrirModalExcluir(botao) {
  const form = document.getElementById('formExcluir');
  form.action = botao.getAttribute('data-url');
  document.getElementById('nomeExcluir').textContent = botao.getAttribute('data-nome') || '';
}
