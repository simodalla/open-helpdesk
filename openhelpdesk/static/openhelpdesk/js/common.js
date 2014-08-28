if('__helpdeskStaticAppPath' in window) {
    requirejs.config({
        baseUrl: __helpdeskStaticAppPath + '/lib',
        paths: {
            app: '..'
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
} else {
    alert('A system error is occurs. Contact the system administrator.');
    window.location.replace(ADMIN_URL);
}