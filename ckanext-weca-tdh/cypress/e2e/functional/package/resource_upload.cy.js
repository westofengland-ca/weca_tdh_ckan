describe('Upload file page', () => {

  before(() => {
    cy.deleteAllData()
    cy.createTestData()
    
  })

  after(() => {
    cy.deleteTestData()
    cy.logoutUser('user/login')
  })

  beforeEach(() => {
    cy.fixture('datasets.json').then((datasets) => {
      // login
      cy.loginUser(`dataset/${datasets[0].name}/upload_form/${datasets[0].resources[0].id}`)
    })
  })

  it('should display all form fields', () => {
    cy.get('#field-resource-upload').should('exist');
    cy.get('#field-author').should('exist');
    cy.get('#field-author-email').should('exist');
    cy.get('#field-description').should('exist');
    cy.get('#submit-button').should('exist');
  });

  it('should not submit form if required fields are empty', () => {
    let submitted = false
    cy.get('#form-upload').invoke('submit', (e) => {
      // do not actually submit the form
      e.preventDefault()
      submitted = true
    })

    cy.get('#form-upload').within(() => {
      cy.get('#field-resource-upload').then($el => $el[0].checkValidity()).should('be.false')
      cy.get('#field-resource-upload').invoke('prop', 'validationMessage')
        .should('equal', 'Please select a file.')

      cy.get('#field-author').then($el => $el[0].checkValidity()).should('be.false')
      cy.get('#field-author').invoke('prop', 'validationMessage')
        .should('equal', 'Please fill in this field.')

      cy.get('#field-author-email').then($el => $el[0].checkValidity()).should('be.false')
      cy.get('#field-author-email').invoke('prop', 'validationMessage')
        .should('equal', 'Please fill in this field.')

      cy.get('#submit-button').click()
    }).then(() => {
      expect(submitted, 'form submitted').to.be.false
    })
  });

  it('should submit form when all required fields are filled', () => {
    let submitted = false
    cy.get('#form-upload').invoke('submit', (e) => {
      // do not actually submit the form
      e.preventDefault()
      submitted = true
    })

    cy.get('#form-upload').within(() => {
      cy.get('#field-resource-upload').selectFile('cypress/fixtures/datasets.json') // Attach a file
        .then($el => $el[0].checkValidity()).should('be.true');
      cy.get('#field-resource-upload').invoke('prop', 'validationMessage')
        .should('equal', '')    
        
      cy.get('#field-author').type('John Doe')
        .then($el => $el[0].checkValidity()).should('be.true'); // Fill author field
      cy.get('#field-author').invoke('prop', 'validationMessage')
        .should('equal', '')    

      cy.get('#field-author-email').type('john@example.com')
        .then($el => $el[0].checkValidity()).should('be.true'); // Fill author email field
      cy.get('#field-author-email').invoke('prop', 'validationMessage')
        .should('equal', '')

      cy.get('#submit-button').click()
    }).then(() => {
      expect(submitted, 'form submitted').to.be.true
    })
  })
})
