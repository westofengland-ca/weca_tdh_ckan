describe('Topic list page', () => {
  before(() => {
    cy.deleteAllData()
    cy.createTestData()
  })

  after(() => {
    cy.deleteTestData()
  })

  beforeEach(() => {
    cy.visit('/group')
  })

  it("sort search results", () => {
    cy.fixture('topics.json').then((topics) => {
      // sort the topics alphabetically
      topics = topics.sort((a, b) => a.title.localeCompare(b.title))

      // name descending
      cy.get('[data-cy="search-sort"]').select(1)
      cy.get('.media-heading').first().should("contain.text", topics[topics.length-1].title)

      // name ascending
      cy.get('[data-cy="search-sort"]').select(0)
      cy.get('.media-heading').first().should("contain.text", topics[0].title)
    })
  })

  it('search for a topic', () => {
    cy.fixture('topics.json').then((topics) => {
      cy.get('[data-cy="results-summary"]').should("contain.text", topics.length)
      cy.get('[data-cy="search-input"]').should('have.attr', 'placeholder', 'Search topics...')
      cy.get('[data-cy="search-input"]').type(topics[0].title)
      cy.get('[data-cy="search-input"]').should("have.value", topics[0].title)
  
      cy.get('[data-cy="search-button"]').click()
      cy.url().should('eq', Cypress.config().baseUrl + 'group?q=' + topics[0].title +'&sort=name+asc')
  
      cy.get('[data-cy="results-summary"]').should("contain.text", topics[0].title)
      cy.get('.group-listclass').find('li').its('length').should("equal", 1)
  
      cy.get('li .media-heading').should("contain.text", topics[0].title)
      cy.get('li .media-description').should("contain.text", topics[0].description)

      cy.fixture('datasets.json').then((datasets) => {
        // get the num of datasets that belong to the topic
        const datasetCount = datasets.filter(x => x.groups.some(group => group.name == topics[0].name)).length
        cy.get('li .count').should("contain.text", datasetCount)
      })

      // click on first topic
      cy.get('li .media-view').click()
      cy.url().should('eq', Cypress.config().baseUrl + 'group/' + topics[0].name)
    })
  })
})
