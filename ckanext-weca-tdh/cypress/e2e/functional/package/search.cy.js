describe("Dataset search page", () => {
  before(() => {
    cy.createTestData()
  })

  after(() => {
    cy.deleteTestData()
  })

  beforeEach(() => {
    cy.visit('/dataset')
  })

  it("sort search results", () => {
    cy.get('[data-cy="filter-groups"]').select("e2e Test")
    cy.get('[data-cy="filter-button"]').click()

    // name descending
    cy.get('[data-cy="search-sort"]').select(2)
    cy.get('.dataset-heading').first().should("contain", "Train stop locations")
    
    // name ascending
    cy.get('[data-cy="search-sort"]').select(1)
    cy.get('.dataset-heading').first().should("contain", "Bus network usage")

    // last modified
    cy.get('[data-cy="search-sort"]').select(3)
    cy.get('.dataset-heading').first().should("contain", "Bus network usage") 
  })

  it("filter datasets using keywords", () => {
    const searchQuery = "Bus"

    cy.get('[data-cy="search-input"]').should('have.attr', 'placeholder', 'Search Transport Data Hub')
    cy.get('[data-cy="search-input"]').type(searchQuery)
    cy.get('[data-cy="search-input"]').should("have.value", searchQuery)

    cy.get('[data-cy="search-button"]').click()

    cy.get('[data-cy="results-summary"]').should("contain", searchQuery)
    cy.get('.dataset-heading').should("contain", searchQuery)
  })

  it("filter datasets using search facets", () => {
    cy.get('[data-cy="filter-organization"]').select("Plymouth Council (e2e)")
    cy.get('[data-cy="filter-groups"]').select("Train (e2e)")
    cy.get('[data-cy="filter-res_format"]').select("CSV")
    
    cy.get('[data-cy="filter-button"]').click()
    cy.get('.dataset-heading').first().should("contain", "Train stop locations")

    // clear filters
    cy.get('[data-cy="filter-remove"]').click()
  })
})
