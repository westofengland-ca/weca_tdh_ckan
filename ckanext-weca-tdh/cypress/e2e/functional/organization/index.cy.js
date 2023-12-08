describe('Publisher list page', () => {
  before(() => {
    cy.deleteAllData()
    cy.createTestData()
  })

  after(() => {
    cy.deleteTestData()
  })

  beforeEach(() => {
    cy.visit('/organization')
  })

  it("sort search results", () => {
    cy.fixture('publishers.json').then((publishers) => {
      // sort the publishers alphabetically
      publishers = publishers.sort((a, b) => a.title.localeCompare(b.title))

      // name descending
      cy.get('[data-cy="search-sort"]').select(1)
      cy.get('.media-heading').first().should("contain.text", publishers[publishers.length-1].title)

      // name ascending
      cy.get('[data-cy="search-sort"]').select(0)
      cy.get('.media-heading').first().should("contain.text", publishers[0].title)
    })
  })

  it('search for a publisher', () => {
    cy.fixture('publishers.json').then((publishers) => {
      cy.get('[data-cy="results-summary"]').should("contain.text", publishers.length)
      cy.get('[data-cy="search-input"]').should('have.attr', 'placeholder', 'Search publishers...')
      cy.get('[data-cy="search-input"]').type(publishers[0].title)
      cy.get('[data-cy="search-input"]').should("have.value", publishers[0].title)
  
      cy.get('[data-cy="search-button"]').click()
      cy.url().should('eq', Cypress.config().baseUrl + 'organization?q=' + publishers[0].title +'&sort=name+asc')
  
      cy.get('[data-cy="results-summary"]').should("contain.text", publishers[0].title)
      cy.get('.group-listclass').find('li').its('length').should("equal", 1)
  
      cy.get('li .media-heading').should("contain.text", publishers[0].title)
      cy.get('li .media-description').should("contain.text", publishers[0].description)

      cy.fixture('datasets.json').then((datasets) => {
          // get the num of datasets that belong to the publisher
          const datasetCount = datasets.filter(x => x.owner_org == publishers[0].name).length
          cy.get('li .count').should("contain.text", datasetCount)
      })

      // click on first publisher
      cy.get('li .media-view').click()
      cy.url().should('eq', Cypress.config().baseUrl + 'organization/' + publishers[0].name)
    })
  })
})
