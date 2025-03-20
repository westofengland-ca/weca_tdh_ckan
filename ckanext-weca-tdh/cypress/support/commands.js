// 
// Custom Cypress commands
// Example usage: cy.createTestData()
//

Cypress.Commands.add('deleteAllData', () => {
  const apiKey = Cypress.env('API_KEY');
  const url = Cypress.config().baseUrl;
  const user_id = Cypress.env('CKAN_USERNAME');

  cy.request({
    method: 'GET',
    url: `${url}api/action/package_list`,
    headers: {
      'Authorization': apiKey,
      'User-Agent': 'CKAN-CLI',
    },
  }).then((response) => {
    if (response.status === 200) {
      const datasets = response.body.result;
      datasets.forEach((dataset_name) => {
        // Attempt to delete package collaborator
        cy.request({
          method: 'POST',
          url: `${url}api/action/package_collaborator_delete`,
          failOnStatusCode: false,
          headers: {
            'Authorization': apiKey,
            'Content-Type': 'application/json',
            'User-Agent': 'CKAN-CLI',
          },
          body: {
            id: dataset_name,
            user_id: user_id,
          },
        }).then((collaboratorResponse) => {
          if (collaboratorResponse.status === 200) {
            cy.log(`Collaborator for dataset ${dataset_name} deleted successfully.`);
          } else {
            cy.log(`Collaborator for dataset ${dataset_name} not found or deletion failed.`);
          }
        });

        // Attempt to purge dataset
        cy.request({
          method: 'POST',
          url: `${url}api/action/dataset_purge`,
          failOnStatusCode: false,
          headers: {
            'Authorization': apiKey,
            'Content-Type': 'application/json',
            'User-Agent': 'CKAN-CLI',
          },
          body: {
            id: dataset_name,
          },
        }).then((deleteResponse) => {
          if (deleteResponse.status === 200) {
            cy.log(`Dataset ${dataset_name} purged successfully.`);
          } else {
            cy.log(`Failed to purge dataset ${dataset_name}.`);
          }
        });
      });
    } else {
      cy.log('Failed to fetch datasets.');
    }
  })

  cy.request({
    method: 'GET',
    url: `${url}api/action/group_list`,
    headers: {
      'Authorization': apiKey,
      'User-Agent': 'CKAN-CLI'
    },
  }).then(response => {
    if (response.status == 200) {
      const groups = response.body.result;
      groups.forEach((group_name) => {
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
            id: group_name
          }
        }).then(deleteResponse => {
          if (deleteResponse.status === 200) {
            cy.log(`Group ${group_name} purged successfully.`)
          } else {
            cy.log(`Failed to purge group ${group_name}.`)
          }
        })
      })
    } else {
        cy.log('Failed to fetch groups.');
    }
  })

  cy.request({
    method: 'GET',
    url: `${url}api/action/organization_list`,
    headers: {
      'Authorization': apiKey,
      'User-Agent': 'CKAN-CLI'
    },
  }).then(response => {
    if (response.status == 200) {
      const organizations = response.body.result;
      organizations.forEach((organization_name) => {
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
            id: organization_name
          }
        }).then(deleteResponse => {
          if (deleteResponse.status === 200) {
            cy.log(`Organization ${organization_name} purged successfully.`)
          } else {
            cy.log(`Failed to purge organization ${organization_name}.`)
          }
        })
      })
    } else {
        cy.log('Failed to fetch organizations.');
    }
  })
})

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

Cypress.Commands.add('getPublisherDatasets', (publisher) => {
    cy.fixture('datasets.json').then((datasets) => {
      // get datasets that belong to the publisher
      cy.wrap(datasets.filter(x => x.owner_org == publisher.name)).as('datasets')
    })
})

Cypress.Commands.add('getTopicDatasets', (topic) => {
    cy.fixture('datasets.json').then((datasets) => {
      // get datasets that belong to the topic
      cy.wrap(datasets.filter(x => x.groups.some(group => group.name == topic.name))).as('datasets')
    })
})

Cypress.Commands.add('getPackage', (datasetName) => {
  const apiKey = Cypress.env('API_KEY')
  const url = Cypress.config().baseUrl

  cy.request({
    method: 'GET',
    url: `${url}api/action/package_show`,
    failOnStatusCode: false,
    headers: {
      'Authorization': apiKey,
      'User-Agent': 'CKAN-CLI'
    },
    body: {
      id: datasetName
    }
    
  }).then(response => {
      cy.wrap(response.body.result).as('dataset')
  })
})

Cypress.Commands.add('loginUser', (callback) => {
  const url = Cypress.config().baseUrl

  cy.visit(`${url}/user/login`)
  //cy.get('#flDebugHideToolBarButton').click();
  cy.get('input[id="field-login"]').type(Cypress.env('CKAN_USERNAME'))
  cy.get('input[id="field-password"]').type(Cypress.env('CKAN_PASSWORD'))
  cy.get('[data-cy="login-button"]').click()
  cy.visit(`${url}/${callback}`)
})

Cypress.Commands.add('logoutUser', (callback) => {
  const url = Cypress.config().baseUrl

  cy.visit(`${url}/user/_logout`)
  cy.visit(`${url}/${callback}`)
})
