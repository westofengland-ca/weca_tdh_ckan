describe("Dataset search page", () => {
  before(() => {
    cy.deleteAllData()
    cy.createTestData()
  })

  after(() => {
    cy.deleteTestData()
  })

  beforeEach(() => {
    cy.visit('/dataset')
  })

  it("sort search results", () => {
    cy.fixture('datasets.json').then((datasets) => {
      // relevancy
      cy.get('[data-cy="search-sort"]').select("Relevance")
      cy.get('[data-cy="dataset-title"]').first().should("contain.text", datasets[datasets.length-1].title)

      // sort the datasets alphabetically
      datasets = datasets.sort((a, b) => a.title.localeCompare(b.title))

      // name descending
      cy.get('[data-cy="search-sort"]').select("Name Descending")
      cy.get('[data-cy="dataset-title"]').first().should("contain.text", datasets[datasets.length-1].title)

      // name ascending
      cy.get('[data-cy="search-sort"]').select("Name Ascending", {force: true})
      cy.get('[data-cy="dataset-title"]').first().should("contain.text", datasets[0].title)

      // last modified
      cy.get('[data-cy="search-sort"]').select("Last Modified")
      cy.get('[data-cy="dataset-title"]').first().should("contain.text", datasets[0].title)
    })
  })

  it("filter datasets using keywords", () => {
    const searchQuery = "Bus"

    cy.get('[data-cy="search-input"]').should('have.attr', 'placeholder', 'Search Transport Data Hub...')
    cy.get('[data-cy="search-input"]').type(searchQuery)
    cy.get('[data-cy="search-input"]').should("have.value", searchQuery)

    cy.get('[data-cy="search-button"]').click()

    cy.get('[data-cy="results-summary"]').should("contain", searchQuery)
    cy.get('[data-cy="dataset-title"]').first().should("contain", searchQuery)
  })

  it("filter datasets using search facets", () => {
    cy.get('[data-cy="filter-organization"]').select("Plymouth Council")
    cy.get('[data-cy="filter-groups"]').select("Train")
    cy.get('[data-cy="filter-res_format"]').select("CSV")
    
    cy.get('[data-cy="filter-button"]').click()
    cy.get('[data-cy="dataset-title"]').first().should("contain", "Train stop locations")

    // clear filters
    cy.get('[data-cy="filter-remove"]').click()
  })
})
