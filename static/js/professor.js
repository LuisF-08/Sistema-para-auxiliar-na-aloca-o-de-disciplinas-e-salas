function filtrarTabela() {
  const termo = document.getElementById('searchInput').value.toLowerCase();
  document.querySelectorAll('#tabelaBody tr').forEach(linha => {
    linha.style.display = linha.textContent.toLowerCase().includes(termo) ? '' : 'none';
  });
}

function abrirModalCriar() {
  const form = document.getElementById('formProfessor');
  const modalTitle = document.getElementById('professorModalLabel');
  const submitBtn = form.querySelector('button[type="submit"]');

  modalTitle.textContent = 'Novo Professor';
  submitBtn.textContent = 'Criar registro';
  form.action = form.dataset.createUrl || '';
  form.reset();
  document.getElementById('id_ativo').checked = true;
}

function abrirModalEditar(botao) {
  const form = document.getElementById('formProfessor');
  const modalTitle = document.getElementById('professorModalLabel');
  const submitBtn = form.querySelector('button[type="submit"]');

  modalTitle.textContent = 'Editar Professor';
  submitBtn.textContent = 'Salvar alterações';
  form.action = botao.getAttribute('data-url');

  document.getElementById('id_nome').value = botao.getAttribute('data-nome') || '';
  document.getElementById('id_email').value = botao.getAttribute('data-email') || '';
  document.getElementById('id_especialidade').value = botao.getAttribute('data-especialidade') || '';
  document.getElementById('id_carga').value = botao.getAttribute('data-carga') || '';
  document.getElementById('id_ativo').checked = botao.getAttribute('data-ativo') === '1';
}

function abrirModalExcluir(botao) {
  const form = document.getElementById('formExcluir');
  const alocacoes = parseInt(botao.getAttribute('data-alocacoes') || '0', 10);
  form.action = botao.getAttribute('data-url');
  document.getElementById('nomeExcluir').textContent = botao.getAttribute('data-nome') || '';

  const detalheExcluir = document.getElementById('detalheExcluir');
  if (alocacoes > 0) {
    detalheExcluir.textContent = `Este professor possui ${alocacoes} alocação(ões) no sistema. A exclusão também removerá essas alocações relacionadas.`;
  } else {
    detalheExcluir.textContent = 'Esta ação não pode ser desfeita.';
  }
}
