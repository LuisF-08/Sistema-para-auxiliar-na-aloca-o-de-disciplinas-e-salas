function filtrarTabela() {
  const termo = document.getElementById('searchInput').value.toLowerCase();
  document.querySelectorAll('#tabelaBody tr').forEach(linha => {
    linha.style.display = linha.textContent.toLowerCase().includes(termo) ? '' : 'none';
  });
}

function abrirModalCriar() {
  const form = document.getElementById('formSala');
  const modalTitle = document.getElementById('salaModalLabel');
  const submitBtn = form.querySelector('button[type="submit"]');

  modalTitle.textContent = 'Nova Sala';
  submitBtn.textContent = 'Criar registro';
  form.action = form.dataset.createUrl || '';
  form.reset();
}

function abrirModalEditar(botao) {
  const form = document.getElementById('formSala');
  const modalTitle = document.getElementById('salaModalLabel');
  const submitBtn = form.querySelector('button[type="submit"]');

  modalTitle.textContent = 'Editar Sala';
  submitBtn.textContent = 'Salvar alterações';
  form.action = botao.getAttribute('data-url');

  document.getElementById('id_nome').value = botao.getAttribute('data-nome') || '';
  document.getElementById('id_capacidade').value = botao.getAttribute('data-capacidade') || '';
  document.getElementById('id_tipo').value = botao.getAttribute('data-tipo') || '';
  document.getElementById('id_localizacao').value = botao.getAttribute('data-localizacao') || '';
  document.getElementById('id_recursos').value = botao.getAttribute('data-recursos') || '';
}

function abrirModalExcluir(botao) {
  const form = document.getElementById('formExcluir');
  form.action = botao.getAttribute('data-url');
  document.getElementById('nomeExcluir').textContent = botao.getAttribute('data-nome') || '';
}
