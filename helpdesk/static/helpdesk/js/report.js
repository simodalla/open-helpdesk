$(document).ready(function () {

    ['a.add-another', '.autocomplete-light-widget .remove'].forEach(
        function (elem) { $(elem).remove(); }
    );
    ['_addanother', '_continue'].forEach(
        function (elem) { $("input[name='" + elem + "']").remove(); }
    );
});
