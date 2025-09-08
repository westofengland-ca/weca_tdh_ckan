ckan.module('google_analytics',  function(jQuery, _) {
  return {
    initialize: function () {
      var ga_id = this.options.ga_id

      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}

      gtag('consent', 'default', {
        'ad_storage': 'denied',
        'analytics_storage': 'denied',
        'functionality_storage': 'denied',
        'personalization_storage': 'denied',
        'security_storage': 'denied'
      });

      gtag('js', new Date());
      gtag('config', ga_id, { 'debug_mode':true });

      // Request account
      $(document).on('click', '#ga-request-access-account', function (event) {
        var pagePath = window.location.pathname;

        gtag('event', 'request_access_account', {
          'category': 'Request access - account',
          'page_title': pagePath
        });
      });

      // Request dataset access
      $(document).on('click', '#ga-request-access-data', function (event) {
        var pagePath = window.location.pathname;
        var pageHeading = $('.page-heading').text().trim();

        gtag('event', 'request_access_data', {
          'category': 'Request access - data',
          'page_title': pagePath,
          'resource_title': pageHeading,
        });
      });

      // Submit idea
      $(document).on('click', '#ga-submit-idea', function (event) {
        var pagePath = window.location.pathname;

        gtag('event', 'submit_idea', {
          'category': 'Submit idea',
          'page_title': pagePath,
        });
      });

      // TDH Partner Connect
      $(document).on('click', '#ga-tdh-connect', function (event) {
        var pagePath = window.location.pathname;

        gtag('event', 'tdh_connect_download', {
          'category': 'File download - TDH Connect',
          'page_title': pagePath
        });
      });
    
      // Databricks file download
      $(document).on('click', '#ga-file-download-db', function (event) {
        var resIdMatch = $(this).attr('onclick').match(/start_download\('([^']+)'\)/);
        var resId = resIdMatch ? resIdMatch[1] : 'unknown';
        var pageHeading = $('.page-heading').text().trim();

        gtag('event', 'file_download_db', {
          'category': 'File download - Databricks API',
          'resource_id': resId,
          'resource_title': pageHeading,
        });
      });
    }
  };
});
