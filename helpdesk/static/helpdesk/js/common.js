requirejs.config({
    baseUrl: '/static/helpdesk/js/lib',
    paths: {
        app: '../app'
    },
    map: {
      // '*' means all modules will get 'jquery'
      // for their 'jquery' dependency.
      '*': { 'jquery': 'jquery' },

      // 'jquery' wants the real jQuery module
      // though. If this line was not here, there would
      // be an unresolvable cyclic dependency.
      'jquery': { 'jquery': 'jquery' }
    }
});

define(['jquery'], function (jq) {
    return jq.noConflict( true );
});