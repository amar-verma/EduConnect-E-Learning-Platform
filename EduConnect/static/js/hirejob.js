
document.addEventListener("DOMContentLoaded", function () {
    const checkbox = document.getElementById("terms");
    const button = document.querySelector(".btn-warning");

    // Disable the button by default if the checkbox is not checked
    button.disabled = !checkbox.checked;

    // Add an event listener to enable/disable the button based on checkbox state
    checkbox.addEventListener("change", function () {
        button.disabled = !this.checked;
    });
});
