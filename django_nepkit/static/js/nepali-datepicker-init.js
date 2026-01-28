(function($) {
    "use strict";

    function initNepaliDatePickers() {
        if ($.fn.nepaliDatePicker) {
            // Initialize any date pickers that aren't already initialized
            $(".nepkit-datepicker")
                .not(".nepali-datepicker-initialized")
                .each(function() {
                    $(this)
                        .nepaliDatePicker({
                            dateFormat: "%y-%m-%d",
                            closeOnDateSelect: true,
                            minDate: "१९७५-१-१",
                            maxDate: "२१००-१२-३०",
                        })
                        .addClass("nepali-datepicker-initialized");
                });
        }
    }

    // Initialize on page load
    $(document).ready(function() {
        initNepaliDatePickers();
    });

    // Re-initialize when Django admin adds forms dynamically (e.g., inlines, popups)
    // This handles Django admin's dynamic form loading
    if (typeof django !== "undefined" && django.jQuery) {
        django.jQuery(document).on("formset:added", function() {
            initNepaliDatePickers();
        });
    }

    // Also listen for DOM changes (for admin popups and other dynamic content)
    if (typeof MutationObserver !== "undefined") {
        var observer = new MutationObserver(function(mutations) {
            initNepaliDatePickers();
        });
        observer.observe(document.body, {
            childList: true,
            subtree: true,
        });
    }
})(window.jQuery || window.django.jQuery);
