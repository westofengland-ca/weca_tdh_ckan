ckan.module('cookie_control', function (jQuery) {
  return {
    initialize: function () {

      ckan_sandbox = this.sandbox;

      var config = {
          apiKey: this.options.api_key,
          product: this.options.license_type,
          position: 'right',
          initialState: "notify",
          setInnerHTML: true,
          text: {
            title: "This site uses cookies",
            intro: "Some of these cookies are essential, while others help us to improve your experience by providing insights into how the site is being used. "
                  + "<p>For more information see our <a class='ccc-link ccc-tabbable' href='/policy'>Cookie Policy</a>.</p>",
            acceptSettings: "Accept Recommended Settings",
            rejectSettings: "Reject All",
            accept: "Accept",
            reject: "Reject",
            settings: "Cookie Preferences"
          },
          branding: {
            backgroundColor: "#354753",
            fontFamily: "GDS Transport",
            fontColor: "",
            fontSizeTitle: "26px",
            fontSizeHeaders: "20px",
            fontSize: "18px",  
            toggleText: "black",
            toggleBackground: "white",
            toggleColor: "#354753"
          },
          accessibility: {
            highlightFocus: true,
            outline: true
          },
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
