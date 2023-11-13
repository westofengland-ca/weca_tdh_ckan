ckan.module('google_analytics',  function(jQuery, _) {
  return {
    initialize: function () {

      ga_id = this.options.ga_id

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
      gtag('config', ga_id);
    }
  }
});
