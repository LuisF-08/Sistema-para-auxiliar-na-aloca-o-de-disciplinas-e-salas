function inicializarGraficos(rawResponse) {
  const dados = JSON.parse(rawResponse);

  document.getElementById('kpi-total').innerText = dados.total_alocacoes;
  document.getElementById('kpi-conflitos').innerText = dados.conflitos_pendentes;
  document.getElementById('kpi-ocupacao').innerText = dados.taxa_ocupacao + '%';
  document.getElementById('kpi-professores').innerText = dados.professores_sem_alocacao;

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
