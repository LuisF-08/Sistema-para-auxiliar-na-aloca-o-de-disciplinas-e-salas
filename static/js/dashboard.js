function renderDashboard(dados) {
  document.getElementById('kpi-total').innerText = dados.total_alocacoes;
  document.getElementById('kpi-conflitos').innerText = dados.conflitos_pendentes;
  document.getElementById('kpi-ocupacao').innerText = dados.taxa_ocupacao + '%';
  document.getElementById('kpi-professores').innerText = dados.professores_sem_alocacao;

  document.getElementById('kpi-total-note').innerText = `${dados.total_alocacoes} registros ativos`;
  document.getElementById('kpi-conflitos-note').innerText = `${dados.conflitos_criticos} críticos, ${dados.conflitos_avisos} avisos`;
  document.getElementById('kpi-ocupacao-note').innerText = `${dados.salas_alocadas} de ${dados.total_salas} salas ocupadas`;
  document.getElementById('kpi-professores-note').innerText = `de ${dados.total_professores} professores`;
  document.getElementById('status-salas-note').innerText = `${dados.total_salas} salas totais`;

  document.getElementById('legend-alocadas').innerText = dados.salas_alocadas;
  document.getElementById('legend-livres').innerText = dados.salas_livres;
  document.getElementById('legend-manutencao').innerText = dados.salas_manutencao;

  const ctxOcupacao = document.getElementById('chartOcupacao').getContext('2d');
  new Chart(ctxOcupacao, {
    type: 'bar',
    data: {
      labels: ['Seg', 'Ter', 'Qua', 'Qui', 'Sex'],
      datasets: [{
        data: dados.dados_ocupacao_dias,
        backgroundColor: '#2563EB',
        borderRadius: 4,
        barThickness: 24,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { min: 0, max: 100, ticks: { callback: v => v + '%' } },
        x: { grid: { display: false } }
      }
    }
  });

  const ctxStatus = document.getElementById('chartStatusSalas').getContext('2d');
  new Chart(ctxStatus, {
    type: 'doughnut',
    data: {
      datasets: [{
        data: [dados.salas_alocadas, dados.salas_livres, dados.salas_manutencao],
        backgroundColor: ['#2563EB', '#E2E8F0', '#D97706'],
        borderWidth: 0,
        cutout: '75%'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } }
    }
  });
}

function renderDashboardError() {
  document.getElementById('kpi-total-note').innerText = 'Erro ao carregar métricas';
  document.getElementById('kpi-conflitos-note').innerText = 'Erro ao carregar métricas';
  document.getElementById('kpi-ocupacao-note').innerText = 'Erro ao carregar métricas';
  document.getElementById('kpi-professores-note').innerText = 'Erro ao carregar métricas';
  document.getElementById('status-salas-note').innerText = 'Erro ao carregar métricas';
}

function fetchDashboardMetrics() {
  const wrapper = document.getElementById('dashboardMetrics');
  if (!wrapper) {
    return;
  }

  const apiUrl = wrapper.dataset.apiUrl;
  if (!apiUrl) {
    renderDashboardError();
    return;
  }

  fetch(apiUrl)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      return response.json();
    })
    .then(dados => renderDashboard(dados))
    .catch(() => renderDashboardError());
}

window.addEventListener('DOMContentLoaded', fetchDashboardMetrics);
