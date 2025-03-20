describe('Upload file page', () => {

    before(() => {
      cy.deleteAllData()
      cy.createTestData()
      
    })
  
    after(() => {
      cy.deleteTestData()
      cy.logoutUser('user/login')
    })
  
    beforeEach(() => {
    })
  
    it('should display request access button', () => {
        cy.fixture('datasets.json').then((datasets) => {
            // login
            cy.loginUser(`dataset/${datasets[0].name}/resource/${datasets[0].resources[0].id}`)

            cy.get('[data-cy="access-button"]').contains('Request access').click()
                .should('have.attr', 'href', 'https://forms.office.com/e/2qBSFay0aP')
        })
    });

    it('should not display request access button', () => {
        cy.fixture('datasets.json').then((datasets) => {
            // login
            cy.loginUser(`dataset/${datasets[1].name}/resource/${datasets[1].resources[0].id}`)

            cy.get('[data-cy="access-button"]').should('not.exist')
        })
    });
})