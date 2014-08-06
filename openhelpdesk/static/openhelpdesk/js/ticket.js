require(['./common'], function (common) {

    require([ "jquery", "jquery-ui/jquery-ui.min"], function ($) {
        var ticketInfos = "#ticket_infos";
        var tabsIds = ['ticket_data', 'messages', 'changestatuslog'];

        // remove 'add-another' link/button
        $('a.add-another').remove();

        // settings and managements of tabs
        $(ticketInfos).tabs();

        for(var key in tabsIds) {
            $(ticketInfos).css("margin-bottom",
                $(ticketInfos + " #tab_" + tabsIds[key] +
                    " fieldset").css("margin-bottom"));
            $(ticketInfos + " #tab_" + tabsIds[key] +
                    " fieldset").css("margin-bottom", "0");
        }

        $('a.related_ticket, a.view_report').button();

        helpdeskFinalize($);

        if (typeof tinyMCE != 'undefined') {
            tinyMCE.init({

                // main settings
                mode : "specific_textareas",
                editor_selector : "mceEditor",
                theme: "advanced",
                language: "en",
                dialog_type: "window",
                editor_deselector : "mceNoEditor",
                skin: "thebigreason",

                // general settings
                width: '800px',
                height: '150px',
                indentation : '10px',
                fix_list_elements : true,
                remove_script_host : true,
                accessibility_warnings : false,
                object_resizing: false,
                forced_root_block: "p",
                remove_trailing_nbsp: true,

                relative_urls: false,
                convert_urls: false,

                // theme_advanced
                theme_advanced_toolbar_location: "top",
                theme_advanced_toolbar_align: "left",
                theme_advanced_statusbar_location: "",
                theme_advanced_buttons1: "bold,italic,|,link,unlink,|,table,|,bullist,numlist,|,undo,redo,|,formatselect,",
                theme_advanced_buttons2: "",
                theme_advanced_buttons3: "",
                theme_advanced_path: false,
                theme_advanced_blockformats: "p,h1,h2,h3,h4,pre",
                theme_advanced_styles: "[all] clearfix=clearfix;[p] small=small;[img] Image left-aligned=img_left;[img] Image left-aligned (nospace)=img_left_nospacetop;[img] Image right-aligned=img_right;[img] Image right-aligned (nospace)=img_right_nospacetop;[img] Image Block=img_block;[img] Image Block (nospace)=img_block_nospacetop;[div] column span-2=column span-2;[div] column span-4=column span-4;[div] column span-8=column span-8",
                theme_advanced_resizing : true,
                theme_advanced_resize_horizontal : false,
                theme_advanced_resizing_use_cookie : true,
                advlink_styles: "intern=internal;extern=external",

                plugins: "autolink,inlinepopups,contextmenu,tabfocus,searchreplace,paste,table",

                // remove MS Word's inline styles when copying and pasting.
                paste_remove_spans: true,
                paste_auto_cleanup_on_paste : true,
                paste_remove_styles: true,
                paste_remove_styles_if_webkit: true,
                paste_strip_class_attributes: true,

                // don't strip anything since this is handled by bleach
                valid_elements: "+*[*]",
                valid_children: "+button[a]",

                content_css: window.__tinymce_css

            });

        }

    });
});