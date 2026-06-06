(function() {
    'use strict';

    var PLACEHOLDERS = {
        province: { ne: 'प्रदेश छान्नुहोस्', en: 'Select Province' },
        district: { ne: 'जिल्ला छान्नुहोस्', en: 'Select District' },
        municipality: { ne: 'नगरपालिका छान्नुहोस्', en: 'Select Municipality' }
    };

    function getPlaceholder(type, isNepali) {
        var map = PLACEHOLDERS[type];
        return (map && map[isNepali ? 'ne' : 'en']) || '';
    }

    /**
     * Replace the option list of a select element.
     *
     * If ``preserveSelection`` is true, the currently selected value is
     * kept when it also appears in the new option list — this is what
     * lets the admin initialise a preselected form without losing the
     * saved province/district value.
     *
     * If ``dispatchChange`` is true (the default) a synthetic ``change``
     * event is fired so downstream listeners can react. Pass ``false``
     * when the update is happening as part of initialisation to avoid
     * running user-defined change handlers during page load.
     */
    function updateOptions(selectElement, data, placeholder, preserveSelection, dispatchChange) {
        if (!selectElement) return;
        if (dispatchChange === undefined) {
            dispatchChange = true;
        }
        var currentValue = preserveSelection ? selectElement.value : '';
        selectElement.innerHTML = '';

        if (placeholder) {
            var placeholderOpt = document.createElement('option');
            placeholderOpt.value = '';
            placeholderOpt.textContent = placeholder;
            selectElement.appendChild(placeholderOpt);
        }

        var found = false;
        (data || []).forEach(function(item) {
            var opt = document.createElement('option');
            opt.value = item.id;
            opt.textContent = item.text;
            selectElement.appendChild(opt);
            if (currentValue && item.id === currentValue) {
                found = true;
            }
        });

        if (preserveSelection && currentValue) {
            selectElement.value = found ? currentValue : '';
        }

        if (dispatchChange) {
            selectElement.dispatchEvent(new Event('change'));
        }
    }

    function getLocalData(type, parentId, isNepali) {
        if (!window.NEPKIT_DATA) return null;
        var lang = isNepali ? 'ne' : 'en';
        var data = window.NEPKIT_DATA[lang];
        if (!data) return null;
        if (type === 'districts') {
            return data.districts[parentId] || [];
        }
        if (type === 'municipalities') {
            return data.municipalities[parentId] || [];
        }
        return null;
    }

    function getMatchingSelect(container, selector, isNepali) {
        var matches = container.querySelectorAll(selector);
        for (var i = 0; i < matches.length; i++) {
            var el = matches[i];
            if (el.dataset.ne === 'true' === isNepali) {
                return el;
            }
        }
        return null;
    }

    function fetchData(selectElement, paramName, paramValue, placeholderType, isNepali) {
        if (!selectElement.dataset.url) return Promise.resolve();
        var url = selectElement.dataset.url + '?' + paramName + '=' + encodeURIComponent(paramValue);
        if (isNepali) url += '&ne=true';
        if (selectElement.dataset.en === 'true') url += '&en=true';

        return fetch(url)
            .then(function(response) {
                if (!response.ok) {
                    throw new Error('HTTP ' + response.status + ' from ' + url);
                }
                return response.json();
            })
            .then(function(data) {
                updateOptions(selectElement, data, getPlaceholder(placeholderType, isNepali), true);
            })
            .catch(function(err) {
                // Don't swallow fetch errors silently — log them so the
                // empty dropdown the user sees is at least traceable.
                if (window.console && console.error) {
                    console.error(
                        'nepkit: failed to load ' + placeholderType + ' for ' + paramValue + ':',
                        err
                    );
                }
                updateOptions(selectElement, [], getPlaceholder(placeholderType, isNepali), true);
            });
    }

    function updateDependentSelect(childSelect, dataType, parentValue, placeholderType, isNepali, paramName, preserveSelection, dispatchChange) {
        if (!childSelect) return Promise.resolve();
        if (preserveSelection === undefined) preserveSelection = false;
        if (dispatchChange === undefined) dispatchChange = true;

        if (!parentValue) {
            updateOptions(
                childSelect,
                [],
                getPlaceholder(placeholderType, isNepali),
                preserveSelection,
                dispatchChange
            );
            return Promise.resolve();
        }

        var localData = getLocalData(dataType, parentValue, isNepali);
        if (localData) {
            updateOptions(
                childSelect,
                localData,
                getPlaceholder(placeholderType, isNepali),
                preserveSelection,
                dispatchChange
            );
            return Promise.resolve();
        }
        return fetchData(childSelect, paramName, parentValue, placeholderType, isNepali);
    }

    /**
     * Initialise a single form. Walks the chained selects in order
     * (province → district → municipality) and, when a parent already has
     * a value (e.g. when editing an existing record in the admin),
     * filters the child list to match.  ``dispatchChange`` is forced to
     * ``false`` so that init doesn't fire synthetic change events at
     * user-defined listeners.
     */
    function initForm(container) {
        if (!container) return;
        var provinceSelects = container.querySelectorAll('.nepkit-province-select');

        provinceSelects.forEach(function(provinceSelect) {
            var isNepali = provinceSelect.dataset.ne === 'true';
            var formScope = provinceSelect.closest('form') || container;
            var districtSelect = getMatchingSelect(formScope, '.nepkit-district-select', isNepali);
            var municipalitySelect = getMatchingSelect(formScope, '.nepkit-municipality-select', isNepali);

            if (provinceSelect.value) {
                updateDependentSelect(
                    districtSelect,
                    'districts',
                    provinceSelect.value,
                    'district',
                    isNepali,
                    'province',
                    true,
                    false
                );
            } else if (districtSelect) {
                updateOptions(districtSelect, [], getPlaceholder('district', isNepali), false, false);
            }

            if (districtSelect && districtSelect.value) {
                updateDependentSelect(
                    municipalitySelect,
                    'municipalities',
                    districtSelect.value,
                    'municipality',
                    isNepali,
                    'district',
                    true,
                    false
                );
            } else if (municipalitySelect) {
                updateOptions(municipalitySelect, [], getPlaceholder('municipality', isNepali), false, false);
            }
        });

        // District-only forms (no province in the chain).
        var districtOnlySelects = container.querySelectorAll('.nepkit-district-select');
        districtOnlySelects.forEach(function(districtSelect) {
            if (districtSelect.value) {
                var isNepali = districtSelect.dataset.ne === 'true';
                var formScope2 = districtSelect.closest('form') || container;
                var municipalitySelect = getMatchingSelect(formScope2, '.nepkit-municipality-select', isNepali);
                updateDependentSelect(
                    municipalitySelect,
                    'municipalities',
                    districtSelect.value,
                    'municipality',
                    isNepali,
                    'district',
                    true,
                    false
                );
            }
        });
    }

    function init() {
        initForm(document);
    }

    document.addEventListener('change', function(e) {
        if (e.target.matches('.nepkit-province-select')) {
            var province = e.target.value;
            var isNepali = e.target.dataset.ne === 'true';
            var container = e.target.closest('form') || document;
            var districtSelect = getMatchingSelect(container, '.nepkit-district-select', isNepali);
            var municipalitySelect = getMatchingSelect(container, '.nepkit-municipality-select', isNepali);

            if (municipalitySelect) {
                updateOptions(municipalitySelect, [], getPlaceholder('municipality', isNepali), false, true);
            }
            updateDependentSelect(districtSelect, 'districts', province, 'district', isNepali, 'province', false, true);
        }

        if (e.target.matches('.nepkit-district-select')) {
            var district = e.target.value;
            var isNepali2 = e.target.dataset.ne === 'true';
            var container2 = e.target.closest('form') || document;
            var municipalitySelect2 = getMatchingSelect(container2, '.nepkit-municipality-select', isNepali2);
            updateDependentSelect(municipalitySelect2, 'municipalities', district, 'municipality', isNepali2, 'district', false, true);
        }
    });

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Re-initialise on DOM mutations so dynamically-injected forms
    // (admin inlines, htmx swaps, etc.) get the same treatment.
    // We only watch for new <form> / .nepkit-province-select / .nepkit-district-select
    // additions inside a <form> ancestor; everything else is ignored to
    // avoid the O(document) scan on every keystroke.
    if (typeof MutationObserver !== 'undefined' && document.body) {
        var debounceTimer = null;
        var observer = new MutationObserver(function(mutations) {
            var needsInit = false;
            for (var i = 0; i < mutations.length; i++) {
                var added = mutations[i].addedNodes;
                for (var j = 0; j < added.length; j++) {
                    var node = added[j];
                    if (node.nodeType !== 1) continue;
                    if (
                        node.matches && (
                            node.matches('form') ||
                            node.matches('.nepkit-province-select') ||
                            node.matches('.nepkit-district-select') ||
                            (node.querySelector && node.querySelector('.nepkit-province-select, .nepkit-district-select'))
                        )
                    ) {
                        needsInit = true;
                        break;
                    }
                }
                if (needsInit) break;
            }
            if (!needsInit) return;
            if (debounceTimer) clearTimeout(debounceTimer);
            debounceTimer = setTimeout(function() {
                initForm(document);
            }, 50);
        });
        observer.observe(document.body, { childList: true, subtree: true });
    }
})();
