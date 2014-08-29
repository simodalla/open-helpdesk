require(['./common'], function (common) {
    require([ "jquery", "jquery-ui/jquery-ui"], function ($) {

        if ($("div#search_fields_info").length) {
            var search_fields_info = $("div#search_fields_info").html().trim();
            $("#searchbar").attr("title", search_fields_info);
            $("#searchbar").tooltip({track: true});
        }
    });
});