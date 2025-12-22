class DataAccessManager {
  constructor() {
    this.dataAccessSelect = document.querySelector('select[name="resource_data_access"]');
    this.dataLayerWrapper = document.getElementById('data-layer-wrapper');
    this.tdhQueryWrapper = document.getElementById('tdh-query-wrapper');
    this.dataLayerSelect = document.querySelector('select[name="resource_data_layer"]');
    this.tdhCatalogInput = document.getElementById('field-tdh_catalog');
    this.tdhTableInput = document.getElementById('field-tdh_table');
    this.varSiteId = document.getElementById('site-id');
  }

  init() {
    this.toggleWrappers();
    $(this.dataAccessSelect).on('change', () => this.toggleWrappers());
    $(this.dataLayerSelect).on('change', () => this.updateCatalog());
  }

  toggleWrappers() {
    const val = this.dataAccessSelect.value;

    if (val !== 'External Link') {
      this.dataLayerWrapper.style.display = 'block';
      if (!this.dataLayerSelect.value) this.dataLayerSelect.value = 'Wood';
    } else {
      this.dataLayerWrapper.style.display = 'none';
      this.dataLayerSelect.value = 'Wood';
    }

    if (val === 'TDH Query') {
      this.tdhQueryWrapper.style.display = 'block';
      this.updateCatalog();
    } else {
      this.tdhQueryWrapper.style.display = 'none';
      this.tdhCatalogInput.value = '';
      this.tdhCatalogInput.placeholder = '';
      this.tdhTableInput.value = '';
    }
  }

  updateCatalog() {
    if (this.tdhCatalogInput && this.dataLayerSelect && this.varSiteId) {
      const newVal = `${this.dataLayerSelect.value.toLowerCase()}_${this.varSiteId.textContent}`;
      this.tdhCatalogInput.placeholder = newVal;
      this.tdhCatalogInput.value = newVal;
    }
  }
}

class QueryManager {
  constructor() {
    this.varResourceQueries = document.getElementById('resource-queries-data');
    this.queryInputField = document.getElementById('field-resource_queries');
    this.queryModal = document.getElementById('queries-modal');
    this.queryModalAddBtn = document.getElementById('queries-modal-btn-add');
    this.queryModalSaveBtn = document.getElementById('queries-modal-btn-save');
    this.queryModalCancelBtn = document.getElementById('queries-modal-btn-cancel');
    this.queryModalCloseBtn = document.getElementById('queries-modal-btn-close');
    this.queryListLenField = document.getElementById('queries-len');

    this.allowedFormats = ["csv", "json", "parquet"];
    this.queries = [];
    this.initialQueries = [];
  }

  init() {
    this.initialQueries = this.loadInitialQueries();
    this.queries = [...this.initialQueries];
    this.saveChanges();

    this.queryModal.addEventListener('show.bs.modal', () => this.onModalShow());
    this.queryModalAddBtn.addEventListener('click', () => this.addQuery());
    this.queryModalSaveBtn.addEventListener('click', () => this.saveChanges());
    this.queryModalCancelBtn.addEventListener('click', () => this.discardChanges());
    this.queryModalCloseBtn.addEventListener('click', () => this.discardChanges());

    document.querySelector('#modal-accordion')
      .addEventListener('input', e => this.handleInput(e));
    document.querySelector('#modal-accordion')
      .addEventListener('click', e => this.handleClick(e));

    this.initAddFormLiveValidation();
  }

  loadInitialQueries() {
    if (!this.varResourceQueries) return [];
    try {
      const parsed = JSON.parse(this.varResourceQueries.textContent);
      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return [];
    }
  }

  onModalShow() {
    try {
      const val = JSON.parse(this.queryInputField.value || '[]');
      this.queries = Array.isArray(val) ? val : [];
    } catch {
      this.queries = [];
    }
    this.renderTable();
  }

  renderTable() {
    const container = document.getElementById('modal-accordion');
    container.innerHTML = '';

    if (!this.queries.length) {
      container.innerHTML =
        `<p class="text-muted mt-2">No queries have been assigned to this resource. Add a new query below.</p>`;
      return;
    }

    this.queries.forEach((q, index) => {
      const div = document.createElement('div');
      div.className = index === 0 ? '' : 'tdh-query-block';

      const formatOptions = this.allowedFormats.map(fmt => `
        <div class="form-check form-check-inline">
          <input class="form-check-input query-format-checkbox" 
                  type="checkbox"
                  data-index="${index}" 
                  data-field="formats"
                  value="${fmt}" 
                  id="format-${fmt}-${index}"
                  ${q.formats.includes(fmt) ? "checked" : ""}>
          <label class="form-check-label no-after"
                  for="format-${fmt}-${index}" style="font-size:11px;">
            ${fmt.toUpperCase()}
          </label>
        </div>`
      ).join('');

      div.innerHTML = `
        <div class="accordion" id="queryAccordion">
          <div class="accordion-item" id="tdh-query-${index}" style="border:2px solid black;">
            <h2 class="accordion-header" id="heading-${index}">
              <button class="accordion-button collapsed" type="button"
                      data-bs-toggle="collapse" data-bs-target="#collapse-${index}">
                      ${q.title || 'New Query'}
              </button>
            </h2>
            <div id="collapse-${index}" class="accordion-collapse collapse"
                 data-bs-parent="#queryAccordion">
              <div class="accordion-body">
                <div class="mb-2">
                  <label>Title</label>
                  <textarea class="form-control" 
                            data-index="${index}" 
                            data-field="title">${q.title}</textarea>
                </div>
                <div class="mb-2">
                  <label>Summary</label>
                  <textarea class="form-control" 
                            data-index="${index}" 
                            data-field="summary">${q.summary}</textarea>
                </div>
                <div class="mb-2">
                  <label>SQL Query</label>
                  <textarea class="form-control" 
                            data-index="${index}" 
                            data-field="statement">${q.statement}</textarea>
                </div>
                <div class="mb-2">
                  <label>Formats</label>
                  <div>${formatOptions}</div>
                </div>
                <button type="button" class="btn btn-sm btn-danger btn-delete"
                        data-index="${index}">Delete</button>
              </div>
            </div>
          </div>
        </div>
      `;

      container.appendChild(div);

      this.setupFieldValidation(div.querySelector('[data-field="title"]'), [this.validateRequired]);
      this.setupFieldValidation(div.querySelector('[data-field="summary"]'), [this.validateRequired]);
      this.setupFieldValidation(div.querySelector('[data-field="statement"]'), [
        this.validateRequired,
        this.validateSQL
      ]);
    });
  }

  validateRequired(value) {
    return value.trim() ? null : "This field is required.";
  }

  validateSQL(value) {
    const v = value.trim().toUpperCase();
    const forbidden = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "MERGE", "CREATE"];
    return forbidden.some(f => v.includes(f)) ? "Write operations are not allowed." : null;
  }

  validateField(inputEl, validators) {
    let msgEl = inputEl.parentNode.querySelector(".invalid-feedback");
    if (!msgEl) {
      msgEl = document.createElement("div");
      msgEl.className = "invalid-feedback";
      inputEl.parentNode.appendChild(msgEl);
    }

    const value = inputEl.value;
    const error = validators.map(v => v(value)).find(e => e !== null);

    if (error) {
      inputEl.classList.add("is-invalid");
      inputEl.classList.remove("is-valid");
      msgEl.textContent = error;
      return false;
    }

    inputEl.classList.remove("is-invalid");
    inputEl.classList.add("is-valid");
    msgEl.textContent = "";
    return true;
  }

  setupFieldValidation(inputEl, validators) {
    inputEl.addEventListener("input", () => {
      this.validateField(inputEl, validators);
    });
  }

  initAddFormLiveValidation() {
    const titleInput = document.getElementById('query-title');
    const summaryInput = document.getElementById('query-summary');
    const statementInput = document.getElementById('query-statement');

    this.setupFieldValidation(titleInput, [this.validateRequired]);
    this.setupFieldValidation(summaryInput, [this.validateRequired]);
    this.setupFieldValidation(statementInput, [
      this.validateRequired,
      this.validateSQL
    ]);
  }

  addQuery() {
    const titleInput = document.getElementById('query-title');
    const summaryInput = document.getElementById('query-summary');
    const statementInput = document.getElementById('query-statement');

    const inputs = [
      { input: titleInput, validators: [this.validateRequired] },
      { input: summaryInput, validators: [this.validateRequired] },
      { input: statementInput, validators: [this.validateRequired, this.validateSQL] }
    ];

    const allValid = inputs.every(({ input, validators }) =>
      this.validateField(input, validators)
    );

    if (!allValid) return;

    this.queries.push({
      title: titleInput.value.trim(),
      summary: summaryInput.value.trim(),
      statement: statementInput.value.trim(),
      formats: this.getSelectedFormats('input[name="query-formats"]:checked')
    });

    this.renderTable();

    inputs.forEach(({ input }) => {
      input.value = '';
      input.classList.remove('is-valid');
    });

    document.querySelectorAll('input[name="query-formats"]').forEach(cb => {
      cb.checked = cb.value === this.allowedFormats[0];
    });
  }

  getSelectedFormats(selector) {
    return [...document.querySelectorAll(selector)]
      .map(cb => cb.value.toLowerCase());
  }

  handleInput(e) {
    const el = e.target;
    const { index, field } = el.dataset;
    if (index === undefined || !field) return;

    if (field === "formats") {
      this.queries[index].formats = this.getSelectedFormats(
        `input[data-index="${index}"][data-field="formats"]:checked`
      );
    } else {
      this.queries[index][field] = el.value;
    }
  }

  handleClick(e) {
    if (!e.target.classList.contains('btn-delete')) return;
    const idx = e.target.dataset.index;
    this.queries.splice(idx, 1);
    this.renderTable();
  }

  saveChanges() {
    const allFields = document.querySelectorAll(
      '#modal-accordion textarea[data-field]'
    );
    const warningEl = document.getElementById('invalid-fields-warning');

    let allValid = true;
    let firstInvalid = null;

    allFields.forEach(field => {
      const validators = [this.validateRequired];

      if (field.dataset.field === "statement")
        validators.push(this.validateSQL);

      const isValid  = this.validateField(field, validators);
      if (!isValid) {
        allValid = false;
        if (!firstInvalid) firstInvalid = field;
      }
    });

    if (!allValid) {
      warningEl.style.display = 'inline';

      if (firstInvalid) {
        const collapseDiv = firstInvalid.closest('.accordion-collapse');
        if (collapseDiv && !collapseDiv.classList.contains('show')) {
          const bsCollapse = bootstrap.Collapse.getOrCreateInstance(collapseDiv);
          bsCollapse.show();
        }

        setTimeout(() => {
          firstInvalid.scrollIntoView({ behavior: "smooth", block: "center" });
          firstInvalid.focus();
        }, 300);
      }

      return;
    }

    warningEl.style.display = 'none';

    this.queryInputField.value = JSON.stringify(this.queries);

    const len = this.queries.length;
    const plural = len === 1 ? 'query' : 'queries';
    document.getElementById('queries-len').innerText = len;
    document.getElementById('queries-text').innerText = `${plural} assigned to it.`;

    const modalInstance = bootstrap.Modal.getOrCreateInstance(this.queryModal);
    modalInstance.hide();
  }

  discardChanges() {
    this.queries = [...this.initialQueries];
  }
}

document.addEventListener("DOMContentLoaded", function () {
  const dataAccessManager = new DataAccessManager();
  dataAccessManager.init();

  const queryManager = new QueryManager();
  queryManager.init();
});
