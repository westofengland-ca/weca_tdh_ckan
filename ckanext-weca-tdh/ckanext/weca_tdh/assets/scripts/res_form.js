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
      document.querySelector('#modal-accordion').addEventListener('input', e => this.handleInput(e));
      document.querySelector('#modal-accordion').addEventListener('click', e => this.handleClick(e));
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
      const container = document.getElementById('modal-accordion');
      container.innerHTML = '';

      if (this.queries && this.queries.length > 0) {
        this.queries.forEach((q, index) => {
          const queryId = `tdh-query-${index}`;
          const spinnerId = `query-spinner-${index}`;
          const formatOptions = ["csv", "json", "xml", "parquet"].map(fmt => {
            const checked = q.formats.includes(fmt) ? "checked" : "";
            return `<div class="form-check form-check-inline">
                      <input class="form-check-input query-format-checkbox" type="checkbox"
                            data-index="${index}" data-field="formats" value="${fmt}" id="format-${fmt}-${index}" ${checked}>
                      <label class="form-check-label no-after" for="format-${fmt}-${index}" style="font-size:11px;">${fmt.toUpperCase()}</label>
                    </div>`;
          }).join('');

          const div = document.createElement('div');
          div.className = index === 0 ? '' : 'tdh-query-block';

          div.innerHTML = `
            <div class="accordion" id="queryAccordion">
              <div id="${queryId}" class="accordion-item" style="border:2px solid black;">
                <h2 class="accordion-header" id="heading-${index}">
                  <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-${index}">
                    ${q.title || 'New Query'}
                  </button>
                </h2>
                <div id="collapse-${index}" class="accordion-collapse collapse" data-bs-parent="#queryAccordion">
                  <div class="accordion-body">
                    <div class="mb-2">
                      <label>Title</label>
                      <textarea class="form-control" data-index="${index}" data-field="title">${q.title}</textarea>
                    </div>
                    <div class="mb-2">
                      <label>Summary</label>
                      <textarea class="form-control" data-index="${index}" data-field="summary">${q.summary}</textarea>
                    </div>
                    <div class="mb-2">
                      <label>SQL Query</label>
                      <textarea class="form-control" data-index="${index}" data-field="statement">${q.statement}</textarea>
                    </div>
                    <div class="mb-2">
                      <label>Formats</label>
                      <div>
                        ${formatOptions}
                      </div>
                    </div>
                    <button type="button" class="btn btn-sm btn-danger btn-delete" data-index="${index}">Delete</button>
                  </div>
                </div>
              </div>
            </div>
          `;
          container.appendChild(div);
        });
      } else {
        const emptyMessage = document.createElement('p');
        emptyMessage.classList.add('text-muted', 'mt-2');
        emptyMessage.textContent = 'No queries have been assigned to this resource. Add a new query below.';
        container.appendChild(emptyMessage);
      }
    },
    getSelectedFormats(selector) {
      const checkboxes = document.querySelectorAll(selector);
      return Array.from(checkboxes).map(cb => cb.value.toLowerCase());
    },
    addQuery() {
      const title = document.getElementById('query-title').value.trim();
      const summary = document.getElementById('query-summary').value.trim();
      const statement = document.getElementById('query-statement').value.trim();
      const formats = this.getSelectedFormats('input[name="query-formats"]:checked');

      console.log(formats)

      if (!title || !statement) return;

      this.queries.push({ title, summary, statement, formats });
      this.renderTable();

      document.getElementById('query-title').value = '';
      document.getElementById('query-summary').value = '';
      document.getElementById('query-statement').value = '';
      document.querySelectorAll('input[name="query-formats"]').forEach(cb => cb.checked = false);
    },
    handleInput(e) {
      const target = e.target;
      const { index, field } = target.dataset;

      if (index !== undefined && field) {
        if (field === "formats") {
          this.queries[index][field] = this.getSelectedFormats(`input[data-index="${index}"][data-field="formats"]:checked`)
        } else {
          this.queries[index][field] = target.value;
        }
      }
    },
    handleClick(e) {
      console.log(e.target)
      if (e.target.classList.contains('btn-delete')) {
        console.log("here")
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
