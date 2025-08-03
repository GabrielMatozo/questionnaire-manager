// js feito para melhorar a experiência do usuário (melhorias bobas mas que ajudam em questao de UX)

document.addEventListener('DOMContentLoaded', function () {
  // ==================== UTILITÁRIOS ====================
  function clearToasts() {
    const container = document.getElementById('toast-container');
    if (container) container.innerHTML = '';
  }

  function showToast(message, type = 'success') {
    clearToasts();
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        gap: 10px;
      `;
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `alert alert-${type} fade show`;
    toast.style.cssText = `
      min-width: 300px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      border: none;
    `;
    toast.innerHTML = `
      <div class="d-flex justify-content-between align-items-center">
        <span>${message}</span>
        <button type="button" class="btn-close" aria-label="Fechar"></button>
      </div>
    `;

    container.appendChild(toast);

    // Fechar toast manualmente
    toast.querySelector('.btn-close').onclick = () => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 200);
    };

    // Fechar automaticamente após 4 segundos
    setTimeout(() => {
      if (toast.parentNode) {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 200);
      }
    }, 4000);
  }

  function showLoadingSpinner() {
    let spinner = document.getElementById('global-loading-spinner');
    if (!spinner) {
      spinner = document.createElement('div');
      spinner.id = 'global-loading-spinner';
      spinner.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(255,255,255,0.8);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
      `;
      spinner.innerHTML = `
        <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;" role="status">
          <span class="visually-hidden">Carregando...</span>
        </div>
      `;
      document.body.appendChild(spinner);
    }
    spinner.style.display = 'flex';
  }

  function hideLoadingSpinner() {
    const spinner = document.getElementById('global-loading-spinner');
    if (spinner) spinner.style.display = 'none';
  }

  // ==================== GERENCIAMENTO DE OPÇÕES (RESPOSTAS) ====================

  // Função para adicionar nova opção ao formulário de criação
  window.addOption = function () {
    const container = document.getElementById('options-container');
    if (!container) return;

    const newOption = document.createElement('div');
    newOption.className = 'row mb-2 option-row';
    newOption.innerHTML = `
      <div class="col-7">
        <input type="text" class="form-control" name="option_text" placeholder="Texto da opção" required>
      </div>
      <div class="col-3">
        <input type="number" class="form-control normalize-decimal" name="option_weight"
               placeholder="Peso" step="0.1" required>
      </div>
      <div class="col-2">
        <button type="button" class="btn btn-danger btn-sm w-100" onclick="removeOption(this)">×</button>
      </div>
    `;
    container.appendChild(newOption);
    updateRemoveButtons();
    normalizeDecimalInputs(); // Normalizar novos inputs
  };

  // Função para remover opção do formulário de criação
  window.removeOption = function (button) {
    button.closest('.option-row').remove();
    updateRemoveButtons();
  };

  // Função para adicionar opção a pergunta existente
  window.addOptionToQuestion = function (questionId) {
    const form = document.querySelector(`form[data-question-id="${questionId}"]`);
    if (!form) return;

    const optionsContainer = form.querySelector('.options-container');
    if (!optionsContainer) return;

    const newOption = document.createElement('div');
    newOption.className = 'row mb-2 option-row';
    newOption.innerHTML = `
      <div class="col-7">
        <input type="text" class="form-control" name="new_option_text" placeholder="Nova opção" required>
      </div>
      <div class="col-3">
        <input type="number" class="form-control normalize-decimal" name="new_option_weight"
               placeholder="Peso" step="0.1" required>
      </div>
      <div class="col-2">
        <button type="button" class="btn btn-danger btn-sm w-100" onclick="removeNewOption(this)">×</button>
      </div>
    `;
    optionsContainer.appendChild(newOption);
    normalizeDecimalInputs(); // Normalizar novos inputs
  };

  // Função para remover nova opção (não salva ainda)
  window.removeNewOption = function (button) {
    button.closest('.option-row').remove();
  };

  // Atualizar visibilidade dos botões de remover
  function updateRemoveButtons() {
    const optionRows = document.querySelectorAll('#options-container .option-row');
    optionRows.forEach((row) => {
      const removeBtn = row.querySelector('.btn-danger');
      if (removeBtn) {
        removeBtn.style.display = optionRows.length > 1 ? 'block' : 'none';
      }
    });
  }

  // ==================== NORMALIZAÇÃO DE DECIMAIS ====================
  function normalizeDecimalInputs() {
    // Alterar tipo para texto e validar entrada
    document.querySelectorAll('.normalize-decimal').forEach((input) => {
      input.setAttribute('type', 'text');
      input.addEventListener('input', function () {
        // Substituir vírgula por ponto
        this.value = this.value.replace(',', '.');
        // Validar se é um número válido
        if (!/^\d*(\.\d*)?$/.test(this.value)) {
          this.value = this.value.slice(0, -1);
        }
      });
    });
  }

  // ==================== AJAX HELPERS ====================
  async function makeAjaxRequest(url, options = {}) {
    try {
      const response = await fetch(url, {
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          ...options.headers,
        },
        ...options,
      });

      let result;
      try {
        result = await response.json();
      } catch {
        result = { success: false, message: 'Erro inesperado na resposta do servidor' };
      }

      return result;
    } catch (error) {
      console.error('Erro na requisição:', error);
      return { success: false, message: 'Erro de conexão com o servidor' };
    }
  }

  // ==================== ADICIONAR PERGUNTA ====================
  const addForm = document.getElementById('add-question-form');
  if (addForm) {
    addForm.addEventListener('submit', async function (e) {
      e.preventDefault();

      // Validação frontend
      const questionText = addForm.querySelector('textarea[name="question_text"]');
      if (!questionText.value.trim()) {
        showToast('Digite o texto da pergunta!', 'danger');
        questionText.focus();
        return;
      }

      const optionRows = addForm.querySelectorAll('.option-row');
      if (optionRows.length === 0) {
        showToast('Adicione pelo menos uma opção!', 'danger');
        return;
      }

      let valid = true;
      optionRows.forEach((row) => {
        const optText = row.querySelector('input[name="option_text"]');
        const optWeight = row.querySelector('input[name="option_weight"]');

        if (!optText.value.trim()) {
          optText.classList.add('is-invalid');
          valid = false;
        } else {
          optText.classList.remove('is-invalid');
        }

        if (!optWeight.value || isNaN(parseFloat(optWeight.value))) {
          optWeight.classList.add('is-invalid');
          valid = false;
        } else {
          optWeight.classList.remove('is-invalid');
        }
      });

      if (!valid) {
        showToast('Preencha todos os campos corretamente!', 'danger');
        return;
      }

      showLoadingSpinner();
      clearToasts();

      const formData = new FormData(addForm);
      const result = await makeAjaxRequest(addForm.action, {
        method: 'POST',
        body: formData,
      });

      hideLoadingSpinner();

      if (result.success) {
        showToast(result.message || 'Pergunta adicionada com sucesso!', 'success');
        addForm.reset();
        // Remover opções extras, manter apenas uma
        const container = document.getElementById('options-container');
        const rows = container.querySelectorAll('.option-row');
        for (let i = 1; i < rows.length; i++) {
          rows[i].remove();
        }
        updateRemoveButtons();
        setTimeout(() => location.reload(), 1000);
      } else {
        showToast(result.message || 'Erro ao adicionar pergunta', 'danger');
      }
    });
  }

  // ==================== IMPORTAR PERGUNTAS ====================
  const importForm = document.getElementById('import-questions-form');
  if (importForm) {
    importForm.addEventListener('submit', async function (e) {
      e.preventDefault();

      const questionsData = importForm.querySelector('textarea[name="questions_data"]');
      if (!questionsData.value.trim()) {
        showToast('Digite os dados das perguntas!', 'danger');
        questionsData.focus();
        return;
      }

      showLoadingSpinner();
      clearToasts();

      const formData = new FormData(importForm);
      const result = await makeAjaxRequest(importForm.action, {
        method: 'POST',
        body: formData,
      });

      hideLoadingSpinner();

      if (result.success) {
        showToast(result.message || 'Perguntas importadas com sucesso!', 'success');
        importForm.reset();
        setTimeout(() => location.reload(), 1000);
      } else {
        showToast(result.message || 'Erro ao importar perguntas', 'danger');
      }
    });
  }

  // ==================== EDITAR PERGUNTA ====================
  function initEditQuestionEvents() {
    document.querySelectorAll('.edit-question-form').forEach((form) => {
      form.addEventListener('submit', async function (e) {
        e.preventDefault();

        showLoadingSpinner();
        clearToasts();

        const formData = new FormData(form);
        const result = await makeAjaxRequest(form.action, {
          method: 'POST',
          body: formData,
        });

        hideLoadingSpinner();

        if (result.success) {
          showToast(result.message || 'Pergunta atualizada com sucesso!', 'success');
          setTimeout(() => location.reload(), 1000);
        } else {
          showToast(result.message || 'Erro ao salvar pergunta', 'danger');
        }
      });
    });

    // Eventos de exclusão de pergunta
    document.querySelectorAll('.delete-question-btn').forEach((btn) => {
      btn.addEventListener('click', async function () {
        if (!confirm('Tem certeza que deseja excluir esta pergunta?')) return;

        const questionId = btn.getAttribute('data-question-id');

        showLoadingSpinner();
        clearToasts();

        const result = await makeAjaxRequest(`/admin/delete_question/${questionId}`, {
          method: 'POST',
        });

        hideLoadingSpinner();

        if (result.success) {
          showToast(result.message || 'Pergunta excluída com sucesso!', 'success');
          setTimeout(() => location.reload(), 1000);
        } else {
          showToast(result.message || 'Erro ao excluir pergunta', 'danger');
        }
      });
    });

    // Eventos de exclusão de opção
    document.querySelectorAll('.delete-option-btn').forEach((btn) => {
      btn.addEventListener('click', async function () {
        if (!confirm('Tem certeza que deseja excluir esta opção?')) return;

        const optionId = btn.getAttribute('data-option-id');
        const questionId = btn.getAttribute('data-question-id');

        showLoadingSpinner();
        clearToasts();

        const result = await makeAjaxRequest('/delete_option_ajax', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ option_id: optionId, question_id: questionId }),
        });

        hideLoadingSpinner();

        if (result.success || result.message === 'Opção não encontrada.') {
          showToast('Opção excluída com sucesso!', 'success');
          setTimeout(() => location.reload(), 1000);
        } else {
          showToast(result.message || 'Erro ao excluir opção', 'danger');
        }
      });
    });
  }

  // ==================== ALTERAR SENHA ====================
  const passwordForm = document.getElementById('change-password-form');
  if (passwordForm) {
    passwordForm.addEventListener('submit', async function (e) {
      e.preventDefault();

      const newPassword = passwordForm.querySelector('input[name="new_password"]');
      if (!newPassword.value.trim()) {
        showToast('Digite a nova senha!', 'danger');
        newPassword.focus();
        return;
      }

      showLoadingSpinner();
      clearToasts();

      const formData = new FormData(passwordForm);
      const result = await makeAjaxRequest(passwordForm.action, {
        method: 'POST',
        body: formData,
      });

      hideLoadingSpinner();

      if (result.success) {
        showToast(result.message || 'Senha alterada com sucesso!', 'success');
        passwordForm.reset();
      } else {
        showToast(result.message || 'Erro ao alterar senha', 'danger');
      }
    });
  }

  // ==================== EXPORTAR CSV ====================
  const exportBtn = document.getElementById('export-csv-btn');
  if (exportBtn) {
    exportBtn.addEventListener('click', async function (e) {
      e.preventDefault();

      showLoadingSpinner();
      clearToasts();

      try {
        const response = await fetch('/admin/export_resultados_csv', {
          method: 'GET',
          headers: { 'X-Requested-With': 'XMLHttpRequest' },
        });

        hideLoadingSpinner();

        if (!response.ok) throw new Error('Erro ao exportar CSV');

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'resultados.csv';
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);

        showToast('Exportação concluída!', 'success');
      } catch (error) {
        hideLoadingSpinner();
        showToast('Erro ao exportar resultados', 'danger');
      }
    });
  }

  // ==================== APAGAR TODAS AS PERGUNTAS ====================
  window.deleteAllQuestions = async function () {
    if (
      !confirm(
        'ATENÇÃO: Isso irá apagar TODAS as perguntas cadastradas e suas opções. Tem certeza que deseja continuar?'
      )
    ) {
      return;
    }

    showLoadingSpinner();
    clearToasts();

    const result = await makeAjaxRequest('/admin/delete_all_questions', {
      method: 'POST',
    });

    hideLoadingSpinner();

    if (result.success) {
      showToast(result.message || 'Todas as perguntas foram apagadas!', 'success');
      setTimeout(() => location.reload(), 1500);
    } else {
      showToast(result.message || 'Erro ao apagar perguntas', 'danger');
    }
  };

  // ==================== APAGAR TODOS OS RESULTADOS ====================
  window.clearAllResults = async function () {
    if (
      !confirm(
        'ATENÇÃO: Isso irá apagar TODOS os questionários respondidos. Tem certeza que deseja continuar?'
      )
    ) {
      return;
    }

    showLoadingSpinner();
    clearToasts();

    const result = await makeAjaxRequest('/clear_all_results_ajax', {
      method: 'POST',
    });

    hideLoadingSpinner();

    if (result.success) {
      showToast(result.message || 'Todos os resultados foram apagados!', 'success');
      setTimeout(() => location.reload(), 1500);
    } else {
      showToast(result.message || 'Erro ao apagar resultados', 'danger');
    }
  };

  // ==================== INICIALIZAÇÃO ====================
  // Inicializar eventos de edição
  initEditQuestionEvents();

  // Atualizar botões de remover opção
  updateRemoveButtons();

  // Normalizar inputs decimais existentes
  normalizeDecimalInputs();

  // Esconder spinner se estiver visível
  hideLoadingSpinner();
});

// ==================== FORMATAÇÃO DE PESO ====================
document.addEventListener('input', function (e) {
  if (e.target.classList.contains('weight-input')) {
    let value = e.target.value;

    // Permitir apenas números, vírgula e ponto
    value = value.replace(/[^0-9.,]/g, '');

    // Substituir ponto por vírgula para entrada
    value = value.replace(/\./g, ',');

    // Permitir apenas uma vírgula
    const parts = value.split(',');
    if (parts.length > 2) {
      value = parts[0] + ',' + parts.slice(1).join('');
    }

    // Limitar casas decimais a 1
    if (parts[1] && parts[1].length > 1) {
      value = parts[0] + ',' + parts[1].substring(0, 1);
    }

    e.target.value = value;
  }
});

// Antes do submit, converter vírgulas para pontos
document.addEventListener('submit', function (e) {
  const form = e.target;
  const weightInputs = form.querySelectorAll('.weight-input');

  weightInputs.forEach((input) => {
    if (input.value) {
      input.value = input.value.replace(',', '.');
    }
  });
});

// ==================== FUNÇÃO GLOBAL PARA VERIFICAR E DELETAR OPÇÃO ====================
function checkAndDeleteOption(button) {
  const questionId = button.getAttribute('data-question-id');
  const optionId = button.getAttribute('data-option-id');

  // Contar quantas opções existem para esta pergunta
  const questionForm = button.closest('form');
  const optionRows = questionForm.querySelectorAll('.option-row');

  if (optionRows.length <= 1) {
    showToast('Não é possível excluir a única opção da pergunta!', 'danger');
    return;
  }

  // Fazer requisição AJAX para deletar a opção
  fetch('/delete_option_ajax', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
    },
    body: JSON.stringify({
      option_id: optionId,
      question_id: questionId,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        // Remover a linha da opção do DOM
        const optionRow = button.closest('.option-row');
        optionRow.remove();
        showToast(data.message || 'Opção excluída com sucesso!', 'success');
      } else {
        showToast(data.message || 'Erro ao excluir opção', 'danger');
      }
    })
    .catch((error) => {
      console.error('Erro:', error);
      showToast('Erro ao excluir opção', 'danger');
    });
}
