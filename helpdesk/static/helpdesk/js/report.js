$(document).ready(function () {
    var pending_action = "put_on_pending";
    var input_action_on_ticket = "input[name='action_on_ticket']";
    var content_field = "#id_content";
    var estimated_end_pending_date = "#id_estimated_end_pending_date";

    ['a.add-another', '.autocomplete-light-widget .remove'].forEach(
        function (elem) { $(elem).remove(); }
    );
    ['_addanother', '_continue'].forEach(
        function (elem) { $("input[name='" + elem + "']").remove(); }
    );

    //
    if ($(input_action_on_ticket+':checked').val() == pending_action) {
        $("#fieldset_pending_range_data").show();
    }

    $(estimated_end_pending_date).datepicker({
        showOtherMonths: true,
        selectOtherMonths: true,
        changeMonth: true,
        changeYear: true,
        minDate: "+2D",
        maxDate: "+2Y",
        dateFormat: "yy-mm-dd",
        appendText: " (yyyy-mm-dd)",
        onClose: function (dateText, inst) {
            if (dateText.trim().length > 0) {
                $(this).removeClass("ui-state-highlight");
            }
        }
    });

    $("#alert_for_empty_content").dialog({
        autoOpen: false,
        modal: true,
        buttons: {
            "Ok": function () {
                $(this).dialog("close");
                $(content_field).focus();
            }
        },
        close: function (event, ui) {
            $(content_field).focus();
        }
    });

    $(content_field).focusout(function () {
        var input = $(this);
        if (input.val().trim().length > 0) {
            input.removeClass("ui-state-highlight");
        } else {
            input.addClass("ui-state-highlight");
        }
    });

    $(input_action_on_ticket).click(function() {
        if ($(this).val() == pending_action) {
            $("#fieldset_pending_range_data").show("slow");
            if ($(content_field).val().trim().length == 0) {
                $("#alert_for_empty_content").dialog("open");
                [content_field, estimated_end_pending_date].forEach(
                    function (elem) {
                        $(elem).addClass("ui-state-highlight");
                    }
                );
            }
        } else {
            $("#fieldset_pending_range_data").hide("slow");
        }
    });
});
