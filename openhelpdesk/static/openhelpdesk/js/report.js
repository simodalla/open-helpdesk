require(['./common'], function (common) {
    require([ "jquery", "jquery-ui/jquery-ui.min", "jquery-ui/i18n/jquery.ui.datepicker-it" ], function ($) {
        var pendingAction = "put_on_pending";
        var inputActionOnTicket = "input[name='action_on_ticket']";
        var contentField = "#id_content";
        var estimatedEndPendingDate = "#id_estimated_end_pending_date";

        ['a.add-another', '.autocomplete-light-widget .remove',
            '.related-widget-wrapper-link'].forEach(
            function (elem) {
                $(elem).remove();
            }
        );
        ['_addanother', '_continue'].forEach(
            function (elem) {
                $("input[name='" + elem + "']").remove();
            }
        );

        //
        if ($(inputActionOnTicket + ':checked').val() == pendingAction) {
            $("#fieldset_pending_range_data").show();
        }

        $(estimatedEndPendingDate).datepicker({
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
                    $(contentField).focus();
                }
            },
            close: function (event, ui) {
                $(contentField).focus();
            }
        });

        helpdeskFinalize($);

        $(contentField).focusout(function () {
            var input = $(this);
            if (input.val().trim().length > 0) {
                input.removeClass("ui-state-highlight");
            } else {
                input.addClass("ui-state-highlight");
            }
        });

        $(inputActionOnTicket).click(function () {
            if ($(this).val() == pendingAction) {
                $("#fieldset_pending_range_data").show("slow");
                if ($(contentField).val().trim().length == 0) {
                    $("#alert_for_empty_content").dialog("open");
                    [contentField, estimatedEndPendingDate].forEach(
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
});