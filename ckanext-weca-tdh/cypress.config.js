const { defineConfig } = require("cypress");

module.exports = defineConfig({
  e2e: {
    "baseUrl": "http://127.0.0.1:5000/",
    "env": {
      "API_KEY": "",
      "CKAN_USERNAME": "",
      "CKAN_PASSWORD": "",
    },
    experimentalInteractiveRunEvents: true,
  },
});
