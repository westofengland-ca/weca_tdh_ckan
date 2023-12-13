describe('Product page', () => {

  before(() => {
    cy.deleteAllData()
    cy.createTestData()
  })

  after(() => {
    cy.deleteTestData()
  })

  beforeEach(() => {
    cy.fixture('datasets.json').then((datasets) => {
      cy.getPackage(datasets[0].name)
      cy.visit('/dataset/' + datasets[0].name)
    }) 
  })

  it("display metadata", () => {
    cy.get('@dataset').then(dataset => {
      cy.get('[data-cy="package-title"]').should("contain.text", dataset.title)

      cy.get('[data-cy="package-publisher"]').should("contain.text", dataset.organization.title)

      cy.get('[data-cy="package-topics"]').should("contain.text", dataset.groups[0].title)

      cy.get('[data-cy="package-license"]').should("contain.text", dataset.license_title || 'License not specified')

      cy.get('[data-cy="package-datalake"]').should("contain.text", dataset.datalake_active ? 'Available' : 'Not available')

      cy.get('[data-cy="package-notes"]').should("contain.text", dataset.notes)
    })
  })

  it('view more datasets from publisher', () => {
      cy.get('@dataset').then(dataset => {
        cy.get('[data-cy="publisher-link"]').click()
        cy.url().should('contain', Cypress.config().baseUrl + 'organization/' + dataset.organization.name)
      })
  })

  it('manage a dataset', () => {
    cy.get('@dataset').then(dataset => {
      // when not logged in
      cy.get('.package-manage').should("not.exist")

      // login
      cy.loginUser(`dataset/${dataset.name}`)

      cy.get('.package-manage').should("exist").click()
      cy.url().should('contain', Cypress.config().baseUrl + 'dataset/edit/' + dataset.name)
    })
  })

  it("explore data links", () => {
    cy.get('@dataset').then(dataset => {
      // login
      cy.loginUser(`dataset/${dataset.name}`)

      cy.get('section').get('.data-links').should('exist')
      cy.get('[data-cy="data-table"]').find('td').eq(0).should('contain.text', dataset.resources[0].name)
      cy.get('[data-cy="data-table"]').find('td').eq(1).should('contain.text', dataset.resources[0].format)
    })
  })

  it('view contact section', () => {
    cy.get('section').get('.contact').should('contain.text', 'ftz@westofengland-ca.gov.uk')
  })

  it('view edit section', () => {
    cy.get('@dataset').then(dataset => {
      cy.get('section').get('.edit').find('p').should('contain.text', 'You must have an account to suggest edits to this dataset')

      // login
      cy.loginUser(`dataset/${dataset.name}`)

      cy.get('section').get('.edit').should('not.exist')
    })
  })
})
