document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".custom-multiselect").forEach(function (multiselect) {
    const toggleBtn = multiselect.querySelector(".multiselect-toggle");
    const optionsBox = multiselect.querySelector(".multiselect-options");
    const labelSpan = multiselect.querySelector(".selected-label");
    const hiddenInputsId = multiselect.getAttribute("data-inputs-id");
    const hiddenInputs = document.getElementById(hiddenInputsId);

    // Toggle dropdown
    toggleBtn.addEventListener("click", function () {
      const isOpen = !optionsBox.hasAttribute("hidden");
      optionsBox.toggleAttribute("hidden");
      toggleBtn.setAttribute("aria-expanded", String(!isOpen));
    });

    // Handle selections
    optionsBox.querySelectorAll("input[type=checkbox]").forEach(function (checkbox) {
      checkbox.addEventListener("change", function () {
        const selected = Array.from(optionsBox.querySelectorAll("input:checked")).map(cb => cb.value);

        // Update label
        labelSpan.textContent = selected.length ? selected.join(", ") : "Select options";

        // Update hidden inputs
        if (hiddenInputs) {
          hiddenInputs.innerHTML = "";
          selected.forEach(function (value) {
            const input = document.createElement("input");
            input.type = "hidden";
            input.name = multiselect.getAttribute("data-name");
            input.value = value;
            hiddenInputs.appendChild(input);
          });
        }
      });
    });

    // Close on outside click
    document.addEventListener("click", function (e) {
      if (!multiselect.contains(e.target)) {
        optionsBox.setAttribute("hidden", true);
        toggleBtn.setAttribute("aria-expanded", "false");
      }
    });
  });
});
