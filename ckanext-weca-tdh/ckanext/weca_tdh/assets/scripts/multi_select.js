document.addEventListener("DOMContentLoaded", function () {
    const allCheckboxes = document.querySelectorAll(".govuk-checkboxes input[type='checkbox']");
    const defaultSummaries = {};

    function updateTagContainer(groupName) {
    const filterSummary = document.getElementById(`search-filter-summary-${groupName}`);
    const tagContainer = document.getElementById(`search-filter-tag-input-${groupName}`);
    if (!filterSummary || !tagContainer) return;

    const checkboxes = document.querySelectorAll(`.govuk-checkboxes input[name="${groupName}"]`);
    let checkedCount = 0;

    if (!(groupName in defaultSummaries)) {
        defaultSummaries[groupName] = filterSummary.dataset.defaultSummary || "No filters selected";
    }

    tagContainer.innerHTML = "";

    checkboxes.forEach(cb => {
        if (cb.checked) {
            checkedCount++;
            const label = cb.labels[0]?.innerText || cb.value;

            const tag = document.createElement("span");
            tag.className = "search-filter-tag-pill";
            tag.textContent = label;

            const removeBtn = document.createElement("button");
            removeBtn.type = "button";
            removeBtn.setAttribute("aria-label", `Remove ${label}`);
            removeBtn.setAttribute("data-value", cb.value);
            removeBtn.innerHTML = "&times;";
            removeBtn.onclick = () => {
                cb.checked = false;
                cb.dispatchEvent(new Event("change"));
            };

            tag.prepend(removeBtn);
            tagContainer.appendChild(tag);
        }
    });

    const hasChecked = checkedCount > 0;
    tagContainer.style.display = hasChecked ? "block" : "none";

    filterSummary.textContent = hasChecked
        ? `${checkedCount} filter${checkedCount === 1 ? '' : 's'} selected`
        : defaultSummaries[groupName];
}

    allCheckboxes.forEach(cb => {
        const name = cb.name;
        cb.addEventListener("change", () => updateTagContainer(name));
    });

    // Initial state on page load
    const facetNames = new Set([...allCheckboxes].map(cb => cb.name));
    facetNames.forEach(name => updateTagContainer(name));
});

function toggleCheckboxContainer(containerId) {
    let cbContainer = document.getElementById(containerId);
    if (cbContainer.style.display == 'none' || cbContainer.style.display === '') {
        cbContainer.style.display = 'block';
    }
    else {
        cbContainer.style.display = 'none';
    }
}
