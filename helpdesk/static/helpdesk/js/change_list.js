require([ "jquery", "jquery-ui/jquery-ui", "helpdesk" ], function ($) {

    $("#searchbar").attr("title", "Puoi effettuare ricerche per: contenuto" +
        "del ticket, titolo delle tipologie, nome, cognome, username del" +
        "richiedente");
    $("#searchbar").tooltip({track: true});
});
