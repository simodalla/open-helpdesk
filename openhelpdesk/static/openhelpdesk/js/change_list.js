require(['./common'], function (common) {
    require(["jquery", "jquery-ui/jquery-ui"], function ($) {

        if ($("div#search_fields_info").length) {
            var search_fields_info = $("div#search_fields_info").html().trim();
            $("#searchbar").attr("title", search_fields_info);
            $("#searchbar").tooltip({track: true});
        }

        // $( "input[name^='news']" )
        console.log($("ul#object-tools li a[href^='add']"));
        // console.log($("ul#object-tools li"));
        var add_link = $("ul.object-tools li a[href^='add']");
        var content =
            '<i class="fa fa-plus-circle" aria-hidden="true"></i>&nbsp' +
            add_link.html();
        add_link.html(content);

        $("div.filter div.filterset ul>li>a[href='?']").each(function (index) {
            $(this).attr('href', '?filter_clean=1');
        });
        $("div#changelist-filter div.results a[href='?']").attr(
            'href', '?filter_clean=1');
    });
});