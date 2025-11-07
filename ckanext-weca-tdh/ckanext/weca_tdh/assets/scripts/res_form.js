document.addEventListener("DOMContentLoaded", function() {
   // ======== Data Access / TDH Catalog ========
  const dataAccessSelect = document.querySelector('select[name="resource_data_access"]');
  const dataLayerWrapper = document.getElementById('data-layer-wrapper');
  const tdhQueryWrapper = document.getElementById('tdh-query-wrapper');
  const dataLayerSelect = document.querySelector('select[name="resource_data_layer"]');
  const tdhCatalogInput = document.getElementById('field-tdh_catalog');
  const tdhTableInput = document.getElementById('field-tdh_table');
  const varSiteId = document.getElementById('site-id');

  const dataAccessObj = {
    init() {
      this.toggleWrappers();
      $(dataAccessSelect).on('change', () => this.toggleWrappers());
      $(dataLayerSelect).on('change', () => this.updateCatalog());
    },
    toggleWrappers() {
      const val = dataAccessSelect.value;
      if (val !== 'External Link') {
        dataLayerWrapper.style.display = 'block';
        if (!dataLayerSelect.value) dataLayerSelect.value = 'Wood';
      } else {
        dataLayerWrapper.style.display = 'none';
        dataLayerSelect.value = 'Wood';
      }

      if (val === 'TDH Query') {
        tdhQueryWrapper.style.display = 'block';
        this.updateCatalog();
      } else {
        tdhQueryWrapper.style.display = 'none';
        tdhCatalogInput.value = '';
        tdhCatalogInput.placeholder = '';
        tdhTableInput.value = '';
      }
    },
    updateCatalog() {
      if (tdhCatalogInput && dataLayerSelect && varSiteId) {
        const newVal = `${dataLayerSelect.value.toLowerCase()}_${varSiteId.textContent}`;
        tdhCatalogInput.placeholder = newVal;
        tdhCatalogInput.value = newVal;
      }
    }
  };

  dataAccessObj.init();


  // ======== Query Modal ========
  const varResourceQueries = document.getElementById('resource-queries-data');
  const queryInputField = document.getElementById('field-resource_queries');
  const queryModal = document.getElementById('queries-modal');
  const queryModalAddBtn = document.getElementById('queries-modal-btn-add');
  const queryModalSaveBtn = document.getElementById('queries-modal-btn-save');
  const queryModalCancelBtn = document.getElementById('queries-modal-btn-cancel');
  const queryModalCloseBtn = document.getElementById('queries-modal-btn-close');

  const queryModalObj = {
    queries: [],
    initialQueries: [],
    init() {
      this.initialQueries = this.loadInitialQueries();
      this.queries = this.initialQueries;
      this.saveChanges();

      queryModal.addEventListener('show.bs.modal', () => this.onModalShow());
      queryModalAddBtn.addEventListener('click', () => this.addQuery());
      queryModalSaveBtn.addEventListener('click', () => this.saveChanges());
      queryModalCancelBtn.addEventListener('click', () => this.discardChanges());
      queryModalCloseBtn.addEventListener('click', () => this.discardChanges());
      document.querySelector('#queries-table tbody').addEventListener('input', e => this.handleInput(e));
      document.querySelector('#queries-table tbody').addEventListener('click', e => this.handleClick(e));
    },
    loadInitialQueries() {
      if (!varResourceQueries) return [];
      try {
        const parsed = JSON.parse(varResourceQueries.textContent);
        return Array.isArray(parsed) ? parsed : [];
      } catch {
        return [];
      }
    },
    onModalShow() {
      try {
        this.queries = JSON.parse(queryInputField.value || '[]');
        if (!Array.isArray(this.queries)) this.queries = [];
      } catch {
        this.queries = [];
      }
      this.renderTable();
    },
    renderTable() {
      const tbody = document.querySelector('#queries-table tbody');
      tbody.innerHTML = '';
      this.queries.forEach((q, index) => {
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
    },
    addQuery() {
      const title = document.getElementById('query-title').value.trim();
      const summary = document.getElementById('query-summary').value.trim();
      const statement = document.getElementById('query-statement').value.trim();
      const format = document.getElementById('query-format').value.trim().toLowerCase();
      if (!title || !statement) return;

      this.queries.push({ title, summary, statement, format });
      this.renderTable();
      ['query-title','query-summary','query-statement','query-format'].forEach(id => document.getElementById(id).value = '');
    },
    handleInput(e) {
      const target = e.target;
      const { index, field } = target.dataset;
      if (index !== undefined && field) {
        this.queries[index][field] = target.value;
      }
    },
    handleClick(e) {
      if (e.target.classList.contains('btn-delete')) {
        const index = e.target.dataset.index;
        this.queries.splice(index, 1);
        this.renderTable();
      }
    },
    saveChanges() {
      queryInputField.value = JSON.stringify(this.queries);
    },
    discardChanges() {
      this.queries = this.initialQueries;
    }
  };

  queryModalObj.init();
});
