(function ($) {
    $(document).ready(function () {
        console.log("ready!");
        console.log(django.jQuery("ul.object-tools li"));
        console.log($(location).attr('href'));
        console.log();
        var current_url = $(location).attr('pathname');
        var url = "/admin/helpdesk/ticket/object_tools/?view=" + current_url;
        $.get(url, function (data) {
            var object_tools_ul = $('ul.object-tools');
            for(var key in data) {
                console.log(data[key].foo);
                object_tools_ul.append(
                        '<li><a href="'+ data[key].url +'">' +
                            data[key].text+ '</a></li>');
            }


        }, "json");
    });
})(django.jQuery);