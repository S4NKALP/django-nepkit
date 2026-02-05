(function() {
    'use strict';

    // Placeholder text constants
    const PLACEHOLDERS = {
        province: { ne: 'प्रदेश छान्नुहोस्', en: 'Select Province' },
        district: { ne: 'जिल्ला छान्नुहोस्', en: 'Select District' },
        municipality: { ne: 'नगरपालिका छान्नुहोस्', en: 'Select Municipality' }
    };

    /**
     * Get placeholder text for a specific location type
     */
    function getPlaceholder(type, isNepali) {
        return PLACEHOLDERS[type][isNepali ? 'ne' : 'en'];
    }

    function updateOptions(selectElement, data, placeholder) {
        selectElement.innerHTML = '';
        if (placeholder) {
            const opt = document.createElement('option');
            opt.value = '';
            opt.textContent = placeholder;
            selectElement.appendChild(opt);
        }
        data.forEach(item => {
            const opt = document.createElement('option');
            opt.value = item.id;
            opt.textContent = item.text;
            selectElement.appendChild(opt);
        });
        selectElement.dispatchEvent(new Event('change'));
    }

    function getLocalData(type, parentId, isNepali) {
        if (!window.NEPKIT_DATA) return null;
        const lang = isNepali ? 'ne' : 'en';
        const data = window.NEPKIT_DATA[lang];
        if (!data) return null;

        if (type === 'districts') {
            return data.districts[parentId] || [];
        } else if (type === 'municipalities') {
            return data.municipalities[parentId] || [];
        }
        return null;
    }

    function getMatchingSelect(container, selector, isNepali) {
        const matches = container.querySelectorAll(selector);
        for (let el of matches) {
            const elIsNepali = el.dataset.ne === 'true';
            if (elIsNepali === isNepali) {
                return el;
            }
        }
        return null;
    }

    /**
     * Fetch data from server endpoint
     */
    function fetchData(selectElement, paramName, paramValue, placeholderType, isNepali) {
        if (!selectElement.dataset.url) return;

        let url = selectElement.dataset.url + '?' + paramName + '=' + encodeURIComponent(paramValue);
        if (isNepali) url += '&ne=true';
        if (selectElement.dataset.en === 'true') url += '&en=true';

        fetch(url)
            .then(response => response.json())
            .then(data => {
                updateOptions(selectElement, data, getPlaceholder(placeholderType, isNepali));
            });
    }

    /**
     * Update dependent select element based on parent value
     */
    function updateDependentSelect(childSelect, dataType, parentValue, placeholderType, isNepali, paramName) {
        if (!childSelect) return;

        if (!parentValue) {
            updateOptions(childSelect, [], getPlaceholder(placeholderType, isNepali));
            return;
        }

        const localData = getLocalData(dataType, parentValue, isNepali);

        if (localData) {
            updateOptions(childSelect, localData, getPlaceholder(placeholderType, isNepali));
        } else {
            fetchData(childSelect, paramName, parentValue, placeholderType, isNepali);
        }
    }

    function init() {
        // Initialize province selects
        document.querySelectorAll('.nepkit-province-select').forEach(provinceSelect => {
            const isNepali = provinceSelect.dataset.ne === 'true';
            const container = provinceSelect.closest('form') || document;
            const districtSelect = getMatchingSelect(container, '.nepkit-district-select', isNepali);
            const municipalitySelect = getMatchingSelect(container, '.nepkit-municipality-select', isNepali);

            if (!provinceSelect.value) {
                if (districtSelect && !districtSelect.value) {
                    updateOptions(districtSelect, [], getPlaceholder('district', isNepali));
                }
                if (municipalitySelect && !municipalitySelect.value) {
                    updateOptions(municipalitySelect, [], getPlaceholder('municipality', isNepali));
                }
            }
        });

        // Initialize district selects
        document.querySelectorAll('.nepkit-district-select').forEach(districtSelect => {
            const isNepali = districtSelect.dataset.ne === 'true';
            const container = districtSelect.closest('form') || document;
            const municipalitySelect = getMatchingSelect(container, '.nepkit-municipality-select', isNepali);

            if (!districtSelect.value) {
                if (municipalitySelect && !municipalitySelect.value) {
                    updateOptions(municipalitySelect, [], getPlaceholder('municipality', isNepali));
                }
            }
        });
    }

    document.addEventListener('change', function(e) {
        // Handle province select change
        if (e.target.matches('.nepkit-province-select')) {
            const province = e.target.value;
            const isNepali = e.target.dataset.ne === 'true';
            const container = e.target.closest('form') || document;
            const districtSelect = getMatchingSelect(container, '.nepkit-district-select', isNepali);
            const municipalitySelect = getMatchingSelect(container, '.nepkit-municipality-select', isNepali);

            // Always clear municipality if province changes
            if (municipalitySelect) {
                updateOptions(municipalitySelect, [], getPlaceholder('municipality', isNepali));
            }

            // Update district options
            updateDependentSelect(districtSelect, 'districts', province, 'district', isNepali, 'province');
        }

        // Handle district select change
        if (e.target.matches('.nepkit-district-select')) {
            const district = e.target.value;
            const isNepali = e.target.dataset.ne === 'true';
            const container = e.target.closest('form') || document;
            const municipalitySelect = getMatchingSelect(container, '.nepkit-municipality-select', isNepali);

            // Update municipality options
            updateDependentSelect(municipalitySelect, 'municipalities', district, 'municipality', isNepali, 'district');
        }
    });

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
