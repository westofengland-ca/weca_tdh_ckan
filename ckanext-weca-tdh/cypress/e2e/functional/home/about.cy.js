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
            .should('have.attr', 'href', 'https://forms.office.com/e/GnirTe2sLs')

        cy.get('[data-cy="support-details"]').click()
        cy.url().should('eq', Cypress.config().baseUrl + 'support')
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
            .should('have.attr', 'href', 'https://forms.office.com/e/GnirTe2sLs')

        cy.get('[data-cy="support-details"]').click()
        cy.url().should('eq', Cypress.config().baseUrl + 'support')
    })
    
    it('should display idea submission', () => {
        cy.loginUser('/about')
        cy.get('[data-cy="submit-us-button"]').contains('Submit an idea')
            .should('have.attr', 'href', '/support')

        cy.get('[data-cy="support-details"]').click()
        cy.url().should('eq', Cypress.config().baseUrl + 'support')
    })
})