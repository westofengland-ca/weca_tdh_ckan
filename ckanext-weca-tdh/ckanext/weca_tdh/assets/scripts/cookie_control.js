ckan.module('cookie_control', function (jQuery) {
  return {
    initialize: function () {

      ckan_sandbox = this.sandbox;

      var config = {
          apiKey: this.options.api_key,
          product: this.options.license_type,
          position: 'RIGHT',
          theme: 'DARK',
          necessaryCookies: ['ckan', 'fldt', 'AppServiceAuthSession'],
          optionalCookies: [
            {
                name: 'analytics',
                label: 'Analytical Cookies',
                description: 'Analytical cookies help us to improve our website by collecting and reporting information on its usage.',
                cookies: [],
                onAccept : function(){
                  ckan_sandbox.publish('analytics_enabled', true);
                },
                onRevoke: function(){
                  ckan_sandbox.publish('analytics_enabled', false);
                }
            }
          ],
      };
      CookieControl.load( config );
    }
  };
});
