$(document).ready(function () {

    var currentUrl = $(location).attr('pathname');
    var url = "/admin/helpdesk/ticket/object_tools/?view=" + currentUrl;
    $.get(url, function (data) {
        var objectToolsUl = $('ul.object-tools');
        for (var key in data) {
            if ("url" in data[key] && "id" in data[key]){
                var li = '<li><a href="'+ data[key].url + '"';
                if (data[key].id) {
                    li += ' id="' + data[key].id  + '"';
                }
                objectToolsUl.append(li + '>' + data[key].text+ '</a></li>');
            }
        }
    }, "json");

    // setting of tooltip for input search
    $("#searchbar").attr("title", "Puoi effettuare ricerche per: contenuto" +
        "del ticket, titolo delle tipologie, nome, cognome, username del" +
        "richiedente");
    $("#searchbar").tooltip({
      track: true
    });

});