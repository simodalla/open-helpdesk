$(document).ready(function () {

    var current_url = $(location).attr('pathname');
    var url = "/admin/helpdesk/ticket/object_tools/?view=" + current_url;
    $.get(url, function (data) {
        var object_tools_ul = $('ul.object-tools');
        for(var key in data) {
            object_tools_ul.append(
                    '<li><a href="'+ data[key].url +'">' +
                        data[key].text+ '</a></li>');
        }
    }, "json");

});