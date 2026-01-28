(function() {
    "use strict";

    function updateOptions(selectElement, data, placeholder) {
        selectElement.innerHTML = "";
        if (placeholder) {
            const opt = document.createElement("option");
            opt.value = "";
            opt.textContent = placeholder;
            selectElement.appendChild(opt);
        }
        data.forEach((item) => {
            const opt = document.createElement("option");
            opt.value = item.id;
            opt.textContent = item.text;
            selectElement.appendChild(opt);
        });
        selectElement.dispatchEvent(new Event("change"));
    }

    document.addEventListener("change", function(e) {
        if (e.target.matches(".nepkit-province-select")) {
            const province = e.target.value;
            const container = e.target.closest("form") || document;
            const districtSelect = container.querySelector(
                ".nepkit-district-select",
            );
            const municipalitySelect = container.querySelector(
                ".nepkit-municipality-select",
            );

            if (districtSelect) {
                if (!province) {
                    updateOptions(districtSelect, [], "Select District");
                    if (municipalitySelect)
                        updateOptions(
                            municipalitySelect,
                            [],
                            "Select Municipality",
                        );
                    return;
                }

                const url =
                    districtSelect.dataset.url +
                    "?province=" +
                    encodeURIComponent(province);
                fetch(url)
                    .then((response) => response.json())
                    .then((data) => {
                        updateOptions(districtSelect, data, "Select District");
                    });
            }
        }

        if (e.target.matches(".nepkit-district-select")) {
            const district = e.target.value;
            const container = e.target.closest("form") || document;
            const municipalitySelect = container.querySelector(
                ".nepkit-municipality-select",
            );

            if (municipalitySelect) {
                if (!district) {
                    updateOptions(
                        municipalitySelect,
                        [],
                        "Select Municipality",
                    );
                    return;
                }

                const url =
                    municipalitySelect.dataset.url +
                    "?district=" +
                    encodeURIComponent(district);
                fetch(url)
                    .then((response) => response.json())
                    .then((data) => {
                        updateOptions(
                            municipalitySelect,
                            data,
                            "Select Municipality",
                        );
                    });
            }
        }
    });
})();
