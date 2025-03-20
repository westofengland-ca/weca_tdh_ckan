describe('Home page', () => {
  before(() => {
    cy.deleteAllData()
    cy.createTestData()
  })

  after(() => {
    cy.deleteTestData()
  })

  beforeEach(() => {
    cy.loginUser('/')
  })

  it('display landing information', () => {
    cy.get('[data-cy="landing-heading"]').should('be.visible')
    cy.get('[data-cy="landing-desc"]').should('be.visible')
  })

  it('should download the partner connect file', () => {
    cy.intercept('GET', '/tdh_partner_connect_file').as('downloadFile');

    // Click the button
    cy.get('[data-cy="connect-button"]').contains('Connect with Power BI').click();

    // Wait for the request and validate it
    cy.wait('@downloadFile').then((interception) => {
      expect(interception.response.statusCode).to.eq(200);

      // Validate the response content
      const responseBody = JSON.parse(interception.response.body);

      expect(responseBody).to.have.property('version', '0.1');
      expect(responseBody.connections[0].details.protocol).to.eq('databricks-sql');
    });

    cy.get('[data-cy="connect-details"]').click()
    cy.url().should('eq', Cypress.config().baseUrl + 'tdh_partner_connect')
  });

  it('search for datasets', () => {
    const searchQuery = "Bus"

    cy.get('[data-cy="search-input"]').should('have.attr', 'placeholder', 'Search Transport Data Hub...')
    cy.get('[data-cy="search-input"]').type(searchQuery)
    cy.get('[data-cy="search-input"]').should("have.value", searchQuery)

    cy.get('[data-cy="search-button"]').click()
    cy.url().should('eq', Cypress.config().baseUrl + 'dataset?q=' + searchQuery)

    cy.get('[data-cy="results-summary"]').should("contain.text", searchQuery)
    cy.get('[data-cy="dataset-title"]').should("contain.text", searchQuery)
  })

  it('list featured topics', () => {
    cy.fixture('topics.json').then((topics) => {
      // sort the topics alphabetically
      topics = topics.sort((a, b) => a.title.localeCompare(b.title))

      cy.get('[data-cy="featured-topics"]')
        .find('li').its('length').should("be.gte", 1)

      cy.get('[data-cy="featured-topics"]')
        .find('li').its('length').should("not.be.gt", 5)

      cy.get('[data-cy="featured-topics"]')
        .find('.media-heading').first()
        .contains(topics[0].title)

      cy.get('[data-cy="featured-topics"]')
        .find('.count').first()
        .contains('2 Datasets')

      cy.get('[data-cy="featured-topics"]')
        .find('li').first().click()
      
      cy.url().should('contain', Cypress.config().baseUrl + 'group/' + topics[0].name)
    })
  })

  it('view more topics', () => {
    cy.get('[data-cy="more-topics"]').contains('More Topics').click()
    cy.url().should('contain', Cypress.config().baseUrl + 'group')
  })

  it('list featured publishers', () => {
    cy.fixture('publishers.json').then((publishers) => {
      // sort the publishers alphabetically
      publishers = publishers.sort((a, b) => a.title.localeCompare(b.title))

      cy.get('[data-cy="featured-publishers"]')
        .find('li').its('length').should("be.gte", 1)

      cy.get('[data-cy="featured-publishers"]')
        .find('li').its('length').should("not.be.gt", 5)

      cy.get('[data-cy="featured-publishers"]')
        .find('.media-heading').first()
        .contains(publishers[0].title)

      cy.get('[data-cy="featured-publishers"]')
        .find('.count').first()
        .contains('1 Dataset')

      cy.get('[data-cy="featured-publishers"]')
        .find('li').first().click()
      
      cy.url().should('contain', Cypress.config().baseUrl + 'organization/' + publishers[0].name)
    })
  })

  it('view more publishers', () => {
    cy.get('[data-cy="more-publishers"]').contains('More Publishers').click()
    cy.url().should('contain', Cypress.config().baseUrl + 'organization')
  })
})
