describe('Landing page', () => {
  before(() => {
    cy.deleteAllData()
    cy.createTestData()
  })

  after(() => {
    cy.deleteTestData()
  })

  beforeEach(() => {
    cy.visit('/')
  })

  it('display landing information', () => {
    cy.get('[data-cy="landing-heading"]').should('be.visible')
    cy.get('[data-cy="landing-desc"]').should('be.visible')
  })

  it('search for datasets', () => {
    const searchQuery = "Bus"

    cy.get('[data-cy="search-input"]').should('have.attr', 'placeholder', 'Search Transport Data Hub...')
    cy.get('[data-cy="search-input"]').type(searchQuery)
    cy.get('[data-cy="search-input"]').should("have.value", searchQuery)

    cy.get('[data-cy="search-button"]').click()
    cy.url().should('eq', Cypress.config().baseUrl + 'dataset?q=' + searchQuery)

    cy.get('[data-cy="results-summary"]').should("contain", searchQuery)
    cy.get('.dataset-heading').should("contain", searchQuery)
  })

  it('list most popular topics', () => {
    cy.get('[data-cy="topic-list"]')
      .find('li').its('length').should("be.gte", 1)

    cy.get('[data-cy="topic-list"]')
      .find('li').its('length').should("not.be.gt", 12)

    cy.get('[data-cy="topic-list"]')
      .find('[data-cy="topic-heading"]').first()
      .find('[data-cy="topic-link"]')
      .click()
    
    cy.url().should('contain', Cypress.config().baseUrl + 'group/bus')
  })
})
