// 
// Custom Cypress commands
// Example usage: cy.createTestData()
//

Cypress.Commands.add('createTestData', () => {
  const apiKey = Cypress.env('API_KEY')
  const url = Cypress.config().baseUrl

  cy.fixture('publishers.json').then((publishers) => {
    publishers.forEach((publisher) => {
      cy.request({
        method: 'POST',
        url: `${url}api/action/organization_create`,
        failOnStatusCode: false,
        headers: {
          'Authorization': apiKey,
          'Content-Type': 'application/json',
          'User-Agent': 'CKAN-CLI'
        },
        body: JSON.stringify(publisher)
      })
    })
  })

  cy.fixture('topics.json').then((topics) => {
    topics.forEach((topic) => {
      cy.request({
        method: 'POST',
        url: `${url}api/action/group_create`,
        failOnStatusCode: false,
        headers: {
          'Authorization': apiKey,
          'Content-Type': 'application/json',
          'User-Agent': 'CKAN-CLI'
        },
        body: JSON.stringify(topic)
      })
    })
  })

  cy.fixture('datasets.json').then((datasets) => {
    datasets.forEach((dataset) => {
      cy.request({
        method: 'POST',
        url: `${url}api/action/package_create`,
        failOnStatusCode: false,
        headers: {
          'Authorization': apiKey,
          'Content-Type': 'application/json',
          'User-Agent': 'CKAN-CLI'
        },
        body: JSON.stringify(dataset)
      })
    })
  })
})

Cypress.Commands.add('deleteTestData', () => {
  const apiKey = Cypress.env('API_KEY')
  const url = Cypress.config().baseUrl

  cy.fixture('datasets.json').then((datasets) => {
    datasets.forEach((dataset) => {
      cy.request({
        method: 'POST',
        url: `${url}api/action/dataset_purge`,
        failOnStatusCode: false,
        headers: {
          'Authorization': apiKey,
          'Content-Type': 'application/json',
          'User-Agent': 'CKAN-CLI'
        },
        body: {
          id: dataset.name
        }
      })
    })
  })

  cy.fixture('topics.json').then((topics) => {
    topics.forEach((topic) => {
      cy.request({
        method: 'POST',
        url: `${url}api/action/group_purge`,
        failOnStatusCode: false,
        headers: {
          'Authorization': apiKey,
          'Content-Type': 'application/json',
          'User-Agent': 'CKAN-CLI'
        },
        body: {
          id: topic.name
        }
      })
    })
  })

  cy.fixture('publishers.json').then((publishers) => {
    publishers.forEach((publisher) => {
      cy.request({
        method: 'POST',
        url: `${url}api/action/organization_purge`,
        failOnStatusCode: false,
        headers: {
          'Authorization': apiKey,
          'Content-Type': 'application/json',
          'User-Agent': 'CKAN-CLI'
        },
        body: {
          id: publisher.name
        }
      })
    })
  })
})