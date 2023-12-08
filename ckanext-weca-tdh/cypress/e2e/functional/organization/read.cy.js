describe('Publisher page', () => {

  let publisher;

  before(() => {
    cy.deleteAllData()
    cy.createTestData()
  })

  after(() => {
    cy.deleteTestData()
  })

  beforeEach(() => {
    cy.fixture('publishers.json').then((publishers) => {
      publisher = publishers[1]
      cy.wrap(publisher).as('publisher')
      cy.getPublisherDatasets(publisher)
      cy.visit('/organization/' + publisher.name)
    })
  })

  it("sort datasets", () => {
    cy.get('@datasets').then(datasets => {
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

        // name ascending
        cy.get('[data-cy="search-sort"]').select("Last Modified")
        cy.get('[data-cy="dataset-title"]').first().should("contain.text", datasets[0].title)
    })
  })

  it('search for a dataset', () => {
    cy.get('@publisher').then(publisher => {
      cy.get('@datasets').then(datasets => {
        cy.get('[data-cy="results-summary"]').should("contain.text", datasets.length)
        cy.get('[data-cy="search-input"]').should('have.attr', 'placeholder', 'Search ' + publisher.title)
        cy.get('[data-cy="search-input"]').type(datasets[0].title)
        cy.get('[data-cy="search-input"]').should("have.value", datasets[0].title)
    
        cy.get('[data-cy="search-button"]').click()
        cy.url().should('contain', Cypress.config().baseUrl + 'organization/' + publisher.name + '?q=' + (datasets[0].title).replace(/ /g,"+"))
    
        cy.get('[data-cy="results-summary"]').should("contain.text", datasets[0].title)
        cy.get('.dataset-listclass').find('.dataset-itemclass').its('length').should("equal", 1)
    
        cy.get('[data-cy="dataset-title"]').should("contain.text", datasets[0].title)
        cy.get('[data-cy="dataset-published"]').should("contain.text", publisher.title)
        cy.get('[data-cy="dataset-notes"]').should("contain.text", datasets[0].notes)

        // click on first dataset
        cy.get('[data-cy="dataset-title"]').click()
        cy.url().should('eq', Cypress.config().baseUrl + 'dataset/' + datasets[0].name)
      })
    })
  })
})
