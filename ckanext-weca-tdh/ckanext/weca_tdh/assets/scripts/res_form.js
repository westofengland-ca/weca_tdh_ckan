document.addEventListener("DOMContentLoaded", function() {
  const varResourceQueries = document.getElementById('resource-queries-data');
  const queryInputField = document.getElementById('field-resource_queries');
  const queryModal = document.getElementById('queries-modal');
  const queryModalAddBtn = document.getElementById('queries-modal-btn-add');
  const queryModalSaveBtn = document.getElementById('queries-modal-btn-save');
  const queryModalCancelBtn = document.getElementById('queries-modal-btn-cancel');
  const queryModalCloseBtn = document.getElementById('queries-modal-btn-close');
  let currentQueries = [];

  if (varResourceQueries) {
    try {
      currentQueries = JSON.parse(varResourceQueries.textContent)
      if (!Array.isArray(currentQueries)) currentQueries = [];
    } catch {
      currentQueries = [];
    }
  }

  let queries = currentQueries;
  saveChanges();

  queryModal.addEventListener('show.bs.modal', function() {
    try {
      queries = JSON.parse(queryInputField.value || '[]');
      if (!Array.isArray(queries)) queries = [];
    } catch {
      queries = [];
    }
    renderTable();
  });

  function renderTable() {
    const tbody = document.querySelector('#queries-table tbody');
    tbody.innerHTML = '';
    queries.forEach((q, index) => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><textarea class="form-control form-control-sm" data-index="${index}" data-field="title">${q.title}</textarea></td>
        <td><textarea class="form-control form-control-sm" data-index="${index}" data-field="summary">${q.summary}</textarea></td>
        <td><textarea class="form-control form-control-sm" data-index="${index}" data-field="statement">${q.statement}</textarea></td>
        <td><input type="text" class="form-control form-control-sm" value="${q.format}" data-index="${index}" data-field="format"></td>
        <td><button class="btn btn-sm btn-danger btn-delete" data-index="${index}">Delete</button></td>
      `;
      tbody.appendChild(tr);
    });
  }

  // Add new query
  queryModalAddBtn.addEventListener('click', function() {
    const title = document.getElementById('query-title').value.trim();
    const summary = document.getElementById('query-summary').value.trim();
    const statement = document.getElementById('query-statement').value.trim();
    const format = document.getElementById('query-format').value.trim().toLowerCase();

    if (!title || !statement) return;

    queries.push({ title, summary, statement, format });
    renderTable();

    document.getElementById('query-title').value = '';
    document.getElementById('query-summary').value = '';
    document.getElementById('query-statement').value = '';
    document.getElementById('query-format').value = '';
  });

  // Live table edits
  document.querySelector('#queries-table tbody').addEventListener('input', function(e) {
    const target = e.target;
    const index = target.dataset.index;
    const field = target.dataset.field;
    if (index !== undefined && field) {
      queries[index][field] = target.value;
    }
  });

  // Delete query
  document.querySelector('#queries-table tbody').addEventListener('click', function(e) {
    if (e.target.classList.contains('btn-delete')) {
      const index = e.target.dataset.index;
      queries.splice(index, 1);
      renderTable();
    }
  });

  function saveChanges() {
    queryInputField.value = JSON.stringify(queries);
  }

  function discardChanges() {
    queries = currentQueries;
  }

  queryModalCloseBtn.addEventListener('click', discardChanges);
  queryModalCancelBtn.addEventListener('click', discardChanges);
  queryModalSaveBtn.addEventListener('click', saveChanges);
});

document.addEventListener('DOMContentLoaded', function () {
  const dataAccessSelect = document.querySelector('select[name="resource_data_access"]');
  const dataLayerWrapper = document.getElementById('data-layer-wrapper');
  const tdhQueryWrapper = document.getElementById('tdh-query-wrapper');
  const dataLayerSelect = document.querySelector('select[name="resource_data_layer"]');
  const tdhCatalogInput = document.getElementById('field-tdh_catalog');
  const tdhTableInput = document.getElementById('field-tdh_table');
  const varSiteId = document.getElementById('site-id');

  function toggleWrappers() {
    const val = dataAccessSelect.value;
    if (val != 'External Link') {
      dataLayerWrapper.style.display = 'block';
      if (!dataLayerSelect.value) dataLayerSelect.value = 'Wood';
    } else {
      dataLayerWrapper.style.display = 'none';
      dataLayerSelect.value = 'Wood';
    }

    if (val === 'TDH Query') {
      tdhQueryWrapper.style.display = 'block';
      updateCatalog();
    } else {
      tdhQueryWrapper.style.display = 'none';
      tdhCatalogInput.value = '';
      tdhCatalogInput.placeholder = '';
      tdhTableInput.value = '';
    }
  }

  function updateCatalog() {
    if (tdhCatalogInput && dataLayerSelect) {
        const newVal = dataLayerSelect.value.toLowerCase() + "_" + varSiteId.textContent;
        tdhCatalogInput.placeholder = newVal;
        tdhCatalogInput.value = newVal;
    }
  }

  toggleWrappers();

  $(dataAccessSelect).on('change', toggleWrappers);
  $(dataLayerSelect).on('change', updateCatalog);
});
