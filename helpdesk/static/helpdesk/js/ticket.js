$(document).ready(function () {
    var ticket_infos = "#ticket_infos";
    $(ticket_infos).tabs();
    var tabs_ids = ['messages', 'changestatuslog'];
    for(var key in tabs_ids) {
        $(ticket_infos).css("margin-bottom",
            $(ticket_infos + " #tab_" + tabs_ids[key] +
                " fieldset").css("margin-bottom"));
        $(ticket_infos + " #tab_" + tabs_ids[key] +
                " fieldset").css("margin-bottom", "0");
    }
});
