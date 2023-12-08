describe('Topic page', () => {

  before(() => {
    cy.deleteAllData()
    cy.createTestData()
  })

  after(() => {
    cy.deleteTestData()
  })

  beforeEach(() => {
    cy.fixture('topics.json').then((topics) => {
      let topic = topics[1]
      cy.wrap(topic).as('topic')
      cy.getTopicDatasets(topic)
      cy.visit('/group/' + topic.name)
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

      // last modified
      cy.get('[data-cy="search-sort"]').select("Last Modified")
      cy.get('[data-cy="dataset-title"]').first().should("contain.text", datasets[0].title)
    })
  })

  it('search for a dataset', () => {
    cy.get('@topic').then(topic => {
      cy.get('@datasets').then(datasets => {
        cy.get('[data-cy="results-summary"]').should("contain.text", datasets.length)
        cy.get('[data-cy="search-input"]').should('have.attr', 'placeholder', 'Search ' + topic.title)
        cy.get('[data-cy="search-input"]').type(datasets[0].title)
        cy.get('[data-cy="search-input"]').should("have.value", datasets[0].title)
    
        cy.get('[data-cy="search-button"]').click()
        cy.url().should('contain', Cypress.config().baseUrl + 'group/' + topic.name + '?q=' + (datasets[0].title).replace(/ /g,"+"))
    
        cy.get('[data-cy="results-summary"]').should("contain.text", datasets[0].title)
        cy.get('.dataset-listclass').find('.dataset-itemclass').its('length').should("equal", 1)
    
        cy.get('[data-cy="dataset-title"]').should("contain.text", datasets[0].title)
        cy.get('[data-cy="dataset-published"]').should("not.be.empty")
        cy.get('[data-cy="dataset-notes"]').should("contain.text", datasets[0].notes)

        // click on first dataset
        cy.get('[data-cy="dataset-title"]').click()
        cy.url().should('eq', Cypress.config().baseUrl + 'dataset/' + datasets[0].name)
      })
    })
  })
})
