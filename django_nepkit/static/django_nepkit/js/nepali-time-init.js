(function () {
    'use strict';

    /**
     * Lightweight time-input helper. Validates HH:MM / HH:MM:SS / hh:mm AM-PM
     * and converts English digits to Devanagari when the field is in `ne` mode.
     * Kept intentionally simple so it does not require jQuery.
     *
     * Nepali-digit input (०-९) is normalized to ASCII before validation so
     * users typing on a Nepali keyboard layout don't see spurious errors.
     */
    var TIME_RE = /^([0-9]{1,2}):([0-9]{2})(:([0-9]{2}))?(\s*([AaPp][Mm]))?$/;
    var NEPALI_TO_ASCII = {'०':'0','१':'1','२':'2','३':'3','४':'4','५':'5','६':'6','७':'7','८':'8','९':'9'};
    var ASCII_TO_NEPALI = {'0':'०','1':'१','2':'२','3':'३','4':'४','5':'५','6':'६','7':'७','8':'८','9':'९'};

    function isNepali(el) {
        return el.dataset.ne === 'true';
    }

    function toAsciiDigits(text) {
        return String(text).replace(/[०-९]/g, function (d) { return NEPALI_TO_ASCII[d]; });
    }

    function toNepaliDigits(text) {
        return String(text).replace(/[0-9]/g, function (d) { return ASCII_TO_NEPALI[d]; });
    }

    function validate(rawValue) {
        if (!rawValue) return true;
        var match = TIME_RE.exec(toAsciiDigits(rawValue).trim());
        if (!match) return false;
        var h = parseInt(match[1], 10);
        var m = parseInt(match[2], 10);
        if (m > 59) return false;
        if (match[5]) {
            if (h < 1 || h > 12) return false;
        } else if (h > 23) {
            return false;
        }
        return true;
    }

    function initOne(el) {
        if (el.dataset.nepkitTimeInit === '1') return;
        el.dataset.nepkitTimeInit = '1';

        el.addEventListener('blur', function () {
            if (!el.value) {
                el.classList.remove('nepkit-time-invalid');
                return;
            }
            if (!validate(el.value)) {
                el.classList.add('nepkit-time-invalid');
                return;
            }
            el.classList.remove('nepkit-time-invalid');
            if (isNepali(el)) {
                el.value = toNepaliDigits(el.value);
            }
        });
    }

    function initAll(root) {
        var scope = root || document;
        var nodes = scope.querySelectorAll('.nepkit-time-input:not([data-nepkit-time-init="1"])');
        nodes.forEach(initOne);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () { initAll(); });
    } else {
        initAll();
    }

    if (typeof MutationObserver !== 'undefined' && document.body) {
        new MutationObserver(function () { initAll(); }).observe(document.body, {
            childList: true,
            subtree: true,
        });
    }
})();
