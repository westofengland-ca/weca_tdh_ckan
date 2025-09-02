describe('Landing page', () => {
    before(() => {
    })
  
    after(() => {
    })
  
    beforeEach(() => {

    })

    it('should display account actions', () => {
        cy.visit('/')
        cy.get('[data-cy="login-button"]').contains('Log in').click()
        cy.url().should('contain', Cypress.config().baseUrl + '.auth/login/aad')

        cy.visit('/')
        cy.get('[data-cy="request-button"]').contains('Request account')
            .should('have.attr', 'href')
            .and('contain', 'https://forms.office.com/Pages/ResponsePage.aspx')

        cy.get('[data-cy="support-details"]').click()
        cy.url().should('eq', Cypress.config().baseUrl + 'pages/support')
    })
})

describe('About page', () => {
    before(() => {
    })
    
    after(() => {
    })
    
    beforeEach(() => {
    })

    it('should display account actions', () => {
        cy.visit('/about')
        cy.get('[data-cy="login-button"]').contains('Log in').click()
        cy.url().should('contain', Cypress.config().baseUrl + '.auth/login/aad')

        cy.visit('/about')
        cy.get('[data-cy="request-button"]').contains('Request account')
            .should('have.attr', 'href')
            .and('contain', 'https://forms.office.com/Pages/ResponsePage.aspx')

        cy.get('[data-cy="support-details"]').click()
        cy.url().should('eq', Cypress.config().baseUrl + 'pages/support')
    })
    
    it('should display idea submission', () => {
        cy.loginUser('/about')
        cy.get('[data-cy="submit-us-button"]').contains('Submit idea')
            .should('have.attr', 'href')
            .and('contain', 'https://forms.office.com/Pages/ResponsePage.aspx')

        cy.get('[data-cy="support-details"]').click()
        cy.url().should('eq', Cypress.config().baseUrl + 'pages/support')
    })
})