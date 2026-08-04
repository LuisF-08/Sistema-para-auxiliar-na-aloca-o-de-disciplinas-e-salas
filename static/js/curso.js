function abrirModalCriar() {
  const form = document.getElementById('formCurso');
  const modalTitle = document.getElementById('cursoModalLabel');
  const submitBtn = form.querySelector('button[type="submit"]');

  modalTitle.textContent = 'Novo Curso';
  submitBtn.textContent = 'Criar registro';
  form.action = form.dataset.createUrl || '';
  form.reset();
}

function abrirModalEditar(botao) {
  const form = document.getElementById('formCurso');
  const modalTitle = document.getElementById('cursoModalLabel');
  const submitBtn = form.querySelector('button[type="submit"]');

  modalTitle.textContent = 'Editar Curso';
  submitBtn.textContent = 'Salvar alterações';
  form.action = botao.getAttribute('data-url');

  document.getElementById('id_nome').value = botao.getAttribute('data-nome') || '';
  document.getElementById('id_codigo').value = botao.getAttribute('data-codigo') || '';
  document.getElementById('id_coordenador').value = botao.getAttribute('data-coordenador') || '';
}

function abrirModalExcluir(botao) {
  const form = document.getElementById('formExcluir');
  form.action = botao.getAttribute('data-url');
  document.getElementById('nomeExcluir').textContent = botao.getAttribute('data-nome') || '';
}
