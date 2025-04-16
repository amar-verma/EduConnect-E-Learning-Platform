
// Add toggle functionality to profile image
const profileDropdown = document.getElementById('profileDropdown');
const navAccordion = document.getElementById('navAccordion');

profileDropdown.addEventListener('click', () => {
    // Toggle the visibility of the nav accordion
    if (navAccordion.style.display === 'none' || !navAccordion.style.display) {
        navAccordion.style.display = 'block';
    } else {
        navAccordion.style.display = 'none';
    }
});

// Optional: Close the accordion if clicked outside
window.addEventListener('click', (e) => {
    if (!e.target.closest('.nav-mobile')) {
        navAccordion.style.display = 'none';
    }
});





// Disable zoom using Ctrl + and Ctrl -

document.addEventListener('keydown', function (event) {
    if ((event.ctrlKey || event.metaKey) && (event.key === '+' || event.key === '-' || event.key === '=')) {
        event.preventDefault();
    }
});

document.addEventListener('wheel', function (event) {
    if (event.ctrlKey) {
        event.preventDefault();
    }
}, { passive: false });

document.addEventListener('gesturestart', function (event) {
    event.preventDefault();
});
document.addEventListener('gesturechange', function (event) {
    event.preventDefault();
});
document.addEventListener('gestureend', function (event) {
    event.preventDefault();
});
