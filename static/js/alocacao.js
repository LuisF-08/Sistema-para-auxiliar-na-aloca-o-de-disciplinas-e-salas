let capacidadeSalaSelecionada = 0;

function validarFormulario() {
  const disciplina = document.getElementById('select-disciplina')?.value;
  const turmaSelect = document.getElementById('select-turma');
  const turmaId = turmaSelect?.value;
  const dia = document.getElementById('select-dia')?.value;
  const horario = document.getElementById('select-horario')?.value;
  const professor = document.getElementById('input-professor')?.value;
  const sala = document.getElementById('input-sala')?.value;
  const btnSubmit = document.getElementById('btn-submit-alocacao');
  const alertaCapacidade = document.getElementById('alerta-capacidade');

  let numAlunos = 0;
  if (turmaSelect && turmaSelect.selectedIndex > 0) {
    const selectedOption = turmaSelect.options[turmaSelect.selectedIndex];
    numAlunos = parseInt(selectedOption.getAttribute('data-alunos')) || 0;
    const inputAlunos = document.getElementById('input-alunos');
    if (inputAlunos && !inputAlunos.value) {
      inputAlunos.value = numAlunos;
    }
  }

  let excedeuCapacidade = false;
  if (sala && numAlunos > 0 && capacidadeSalaSelecionada > 0) {
    if (numAlunos > capacidadeSalaSelecionada) {
      excedeuCapacidade = true;
      if (alertaCapacidade) {
        alertaCapacidade.classList.remove('d-none');
        alertaCapacidade.innerText = `⚠️ Atenção: A turma possui ${numAlunos} alunos, mas a sala selecionada suporta apenas ${capacidadeSalaSelecionada} lugares (Será gerado um alerta de conflito).`;
      }
    } else {
      if (alertaCapacidade) alertaCapacidade.classList.add('d-none');
    }
  } else {
    if (alertaCapacidade) alertaCapacidade.classList.add('d-none');
  }

  const formValido = Boolean(
    disciplina && disciplina !== '' &&
    turmaId && turmaId !== '' &&
    dia && dia !== '' &&
    horario && horario !== '' &&
    professor && professor !== '' &&
    sala && sala !== ''
  );

  if (btnSubmit) {
    if (formValido) {
      btnSubmit.disabled = false;
      btnSubmit.style.backgroundColor = '#2563EB';
      btnSubmit.style.cursor = 'pointer';
    } else {
      btnSubmit.disabled = true;
      btnSubmit.style.backgroundColor = '#94A3B8';
      btnSubmit.style.cursor = 'not-allowed';
    }
  }
}

// ===== FILTRO DE HORÁRIOS POR DIA =====
document.getElementById('select-dia')?.addEventListener('change', () => {
  const diaSelecionado = document.getElementById('select-dia').value;
  const selectHorario = document.getElementById('select-horario');

  selectHorario.value = '';
  document.getElementById('sum-horario').innerText = '—';

  const options = selectHorario.querySelectorAll('option');
  options.forEach(opt => {
    if (!opt.value) {
      opt.style.display = '';
      opt.text = diaSelecionado ? 'Selecione o horário' : 'Selecione primeiro o dia';
    } else if (opt.getAttribute('data-dia') === diaSelecionado) {
      opt.style.display = '';
    } else {
      opt.style.display = 'none';
    }
  });

  validarFormulario();
  verificarDisponibilidade();
});

document.getElementById('select-horario')?.addEventListener('change', () => {
  validarFormulario();
  verificarDisponibilidade();
});

document.getElementById('select-disciplina')?.addEventListener('change', validarFormulario);

document.getElementById('select-turma')?.addEventListener('change', () => {
  const turmaSelect = document.getElementById('select-turma');
  if (turmaSelect.selectedIndex > 0) {
    const opt = turmaSelect.options[turmaSelect.selectedIndex];
    const alunos = opt.getAttribute('data-alunos');
    const inputAlunos = document.getElementById('input-alunos');
    if (inputAlunos) inputAlunos.value = alunos;
  }
  validarFormulario();
});

document.getElementById('input-alunos')?.addEventListener('input', validarFormulario);

// ===== VERIFICAR DISPONIBILIDADE VIA API =====
function verificarDisponibilidade() {
  const dia = document.getElementById('select-dia').value;
  const horarioId = document.getElementById('select-horario').value;

  if (!dia || !horarioId) return;

  fetch(`/api/alocacoes/?dia_semana=${encodeURIComponent(dia)}&horario=${horarioId}`)
    .then(res => res.json())
    .then(alocacoes => {
      const professoresOcupados = alocacoes.map(a => typeof a.professor === 'object' ? a.professor.id : a.professor);
      const salasOcupadas = alocacoes.map(a => typeof a.sala === 'object' ? a.sala.id : a.sala);

      document.querySelectorAll('.prof-item').forEach(item => {
        const profId = parseInt(item.getAttribute('data-prof-id'));
        const statusText = item.querySelector('.status-text');
        const statusIcon = item.querySelector('.status-icon');

        if (professoresOcupados.includes(profId)) {
          item.style.cursor = 'pointer';
          item.style.backgroundColor = '#FFFBEB';
          item.style.borderColor = '#FCD34D';
          if (statusText) {
            statusText.className = 'status-text text-warning small fw-semibold';
            statusText.innerText = 'Conflito: Indisponível (Pode gerar alerta)';
          }
          if (statusIcon) {
            statusIcon.className = 'status-icon bi bi-exclamation-triangle text-warning fs-5';
          }
        } else {
          item.style.cursor = 'pointer';
          item.style.backgroundColor = '#FFFFFF';
          item.style.borderColor = '#E2E8F0';
          if (statusText) {
            statusText.className = 'status-text text-success small fw-semibold';
            statusText.innerText = 'Disponível neste horário';
          }
          if (statusIcon) {
            statusIcon.className = 'status-icon bi bi-check-circle text-success fs-5';
          }
        }
      });

      document.querySelectorAll('.room-item').forEach(item => {
        const salaId = parseInt(item.getAttribute('data-sala-id'));
        const badge = item.querySelector('.status-badge');

        if (salasOcupadas.includes(salaId)) {
          item.style.cursor = 'pointer';
          item.style.backgroundColor = '#FFFBEB';
          item.style.borderColor = '#FCD34D';
          if (badge) {
            badge.className = 'status-badge badge bg-warning-subtle text-warning px-2 py-1 rounded-2';
            badge.innerText = 'Ocupada (Permitido)';
          }
        } else {
          item.style.cursor = 'pointer';
          item.style.backgroundColor = '#FFFFFF';
          item.style.borderColor = '#E2E8F0';
          if (badge) {
            badge.className = 'status-badge badge bg-success-subtle text-success px-2 py-1 rounded-2';
            badge.innerText = 'Disponível';
          }
        }
      });
    })
    .catch(err => console.error('Erro ao verificar disponibilidade via API:', err));
}

// ===== SELEÇÃO DE PROFESSOR E SALA =====
function selecionarProf(el, id, nome) {
  document.querySelectorAll('.prof-item').forEach(i => {
    i.style.borderColor = '#E2E8F0';
    i.style.backgroundColor = '#FFFFFF';
  });
  el.style.borderColor = '#0F172A';
  el.style.backgroundColor = '#F8FAFC';
  document.getElementById('input-professor').value = id;
  document.getElementById('sum-professor').innerText = nome;
  validarFormulario();
}

function selecionarSala(el, id, nome, capacidade) {
  document.querySelectorAll('.room-item').forEach(i => {
    i.style.borderColor = '#E2E8F0';
    i.style.backgroundColor = '#FFFFFF';
  });
  el.style.borderColor = '#0F172A';
  el.style.backgroundColor = '#F8FAFC';
  document.getElementById('input-sala').value = id;
  document.getElementById('sum-sala').innerText = `${nome} (${capacidade} lugares)`;
  capacidadeSalaSelecionada = parseInt(capacidade) || 0;
  validarFormulario();
}

// ===== RESUMO DA ALOCAÇÃO =====
function escutarMudanca(idSelect, idResumo) {
  const campo = document.getElementById(idSelect);
  if (!campo) return;

  const atualizar = () => {
    let texto = '—';
    if (campo.tagName === 'SELECT' && campo.selectedIndex > 0) {
      texto = campo.options[campo.selectedIndex].text;
    } else if (campo.value) {
      texto = campo.value;
    }
    const elementoResumo = document.getElementById(idResumo);
    if (elementoResumo) elementoResumo.innerText = texto;
  };

  campo.addEventListener('change', atualizar);
  if (campo.tagName === 'INPUT') {
    campo.addEventListener('input', atualizar);
  }
}

escutarMudanca('select-disciplina', 'sum-disciplina');
escutarMudanca('select-turma', 'sum-turma');
escutarMudanca('select-dia', 'sum-dia');
escutarMudanca('select-horario', 'sum-horario');
escutarMudanca('input-alunos', 'sum-alunos');

validarFormulario();

// ===== VERIFICAR CONFLITOS E SUGESTÕES =====
function verificarConflitos() {
  const turmaId = document.getElementById('select-turma')?.value;
  const professorId = document.getElementById('input-professor')?.value;
  const salaId = document.getElementById('input-sala')?.value;
  const horarioId = document.getElementById('select-horario')?.value;
  const numAlunos = document.getElementById('input-alunos')?.value || 0;

  if (!horarioId || !turmaId) {
    alert('Selecione pelo menos a turma e o horário para verificar conflitos.');
    return;
  }

  const btn = document.getElementById('btn-verificar-conflitos');
  const textoOriginal = btn.innerHTML;
  btn.innerHTML = '<i class="bi bi-arrow-repeat me-1"></i> Verificando...';
  btn.classList.add('btn-verificando');

  const params = new URLSearchParams();
  if (turmaId) params.append('turma_id', turmaId);
  if (professorId) params.append('professor_id', professorId);
  if (salaId) params.append('sala_id', salaId);
  if (horarioId) params.append('horario_id', horarioId);
  if (numAlunos) params.append('num_alunos', numAlunos);

  fetch(`/alocacao/api/sugestoes/?${params.toString()}`)
    .then(res => res.json())
    .then(data => {
      renderizarSugestoes(data);
      btn.innerHTML = textoOriginal;
      btn.classList.remove('btn-verificando');
    })
    .catch(err => {
      console.error('Erro ao verificar conflitos:', err);
      btn.innerHTML = textoOriginal;
      btn.classList.remove('btn-verificando');
    });
}

function renderizarSugestoes(data) {
  const painel = document.getElementById('painel-sugestoes');
  const listaConflitos = document.getElementById('lista-conflitos');
  const blocoSalas = document.getElementById('bloco-sugestoes-salas');
  const listaSalas = document.getElementById('lista-sugestoes-salas');
  const blocoHorarios = document.getElementById('bloco-sugestoes-horarios');
  const listaHorarios = document.getElementById('lista-sugestoes-horarios');
  const semSugestoes = document.getElementById('sem-sugestoes');

  listaConflitos.innerHTML = '';
  listaSalas.innerHTML = '';
  listaHorarios.innerHTML = '';
  blocoSalas.classList.add('d-none');
  blocoHorarios.classList.add('d-none');
  semSugestoes.classList.add('d-none');

  if (!data.conflitos || data.conflitos.length === 0) {
    painel.classList.remove('d-none');
    listaConflitos.innerHTML = `
      <div style="background:#F0FDF4;border:1px solid #86EFAC;border-radius:8px;padding:10px 14px;color:#166534;font-size:13px;">
        <i class="bi bi-check-circle-fill me-1"></i>
        <strong>Nenhum conflito detectado!</strong> A alocação pode ser criada sem problemas.
      </div>`;
    return;
  }

  painel.classList.remove('d-none');
  const icones = { sala: 'bi-building', professor: 'bi-person', turma: 'bi-mortarboard' };
  data.conflitos.forEach(c => {
    const icone = icones[c.tipo] || 'bi-exclamation-triangle';
    listaConflitos.innerHTML += `
      <div class="conflito-badge d-flex align-items-center gap-2">
        <i class="bi ${icone}"></i>
        <span><strong>Conflito de ${c.tipo}:</strong> ${c.mensagem}</span>
      </div>`;
  });

  if (data.sugestoes_salas && data.sugestoes_salas.length > 0) {
    blocoSalas.classList.remove('d-none');
    data.sugestoes_salas.forEach((s, i) => {
      listaSalas.innerHTML += `
        <div class="sugestao-item-sala d-flex justify-content-between align-items-center"
             style="animation-delay: ${i * 0.15}s"
             onclick="aplicarSugestaoSala(${s.id}, '${s.nome}', ${s.capacidade})">
          <div>
            <div class="fw-bold small text-dark">${s.nome}</div>
            <div class="text-muted" style="font-size:12px">${s.tipo || 'Sala'} · ${s.capacidade} lugares${s.localizacao ? ' · ' + s.localizacao : ''}</div>
          </div>
          <button type="button" class="btn-aplicar btn-aplicar-sala">
            <i class="bi bi-check2 me-1"></i>Aplicar
          </button>
        </div>`;
    });
  }

  if (data.sugestoes_horarios && data.sugestoes_horarios.length > 0) {
    blocoHorarios.classList.remove('d-none');
    data.sugestoes_horarios.forEach((h, i) => {
      listaHorarios.innerHTML += `
        <div class="sugestao-item-horario d-flex justify-content-between align-items-center"
             style="animation-delay: ${i * 0.15}s"
             onclick="aplicarSugestaoHorario(${h.id}, '${h.dia_nome}', '${h.horario_inicio}', '${h.horario_fim}')">
          <div>
            <div class="fw-bold small text-dark">${h.dia_nome}</div>
            <div class="text-muted" style="font-size:12px">${h.horario_inicio} – ${h.horario_fim}</div>
          </div>
          <button type="button" class="btn-aplicar btn-aplicar-horario">
            <i class="bi bi-check2 me-1"></i>Aplicar
          </button>
        </div>`;
    });
  }

  if ((!data.sugestoes_salas || data.sugestoes_salas.length === 0) &&
    (!data.sugestoes_horarios || data.sugestoes_horarios.length === 0)) {
    semSugestoes.classList.remove('d-none');
  }

  painel.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function aplicarSugestaoSala(id, nome, capacidade) {
  document.querySelectorAll('.room-item').forEach(item => {
    const salaId = parseInt(item.getAttribute('data-sala-id'));
    if (salaId === id) {
      item.style.borderColor = '#0F172A';
      item.style.backgroundColor = '#F8FAFC';
    } else {
      item.style.borderColor = '#E2E8F0';
      item.style.backgroundColor = '#FFFFFF';
    }
  });
  document.getElementById('input-sala').value = id;
  document.getElementById('sum-sala').innerText = `${nome} (${capacidade} lugares)`;
  capacidadeSalaSelecionada = parseInt(capacidade) || 0;
  document.getElementById('painel-sugestoes').classList.add('d-none');
  validarFormulario();
}

function aplicarSugestaoHorario(id, diaNome, inicio, fim) {
  const selectHorario = document.getElementById('select-horario');
  if (selectHorario) {
    for (let i = 0; i < selectHorario.options.length; i++) {
      if (parseInt(selectHorario.options[i].value) === id) {
        selectHorario.selectedIndex = i;
        break;
      }
    }
    document.getElementById('sum-horario').innerText = `${inicio} – ${fim}`;
  }
  document.getElementById('painel-sugestoes').classList.add('d-none');
  validarFormulario();
  verificarDisponibilidade();
}
