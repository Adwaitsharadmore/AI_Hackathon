// Get the elements
const landingPageContent = document.getElementById('landing-page-content'); // Replace with your actual landing page content section ID (if different)
const statementsSection = document.getElementById('mission-vision'); // Replace with your actual statements section ID

// Initially hide the statements section
statementsSection.classList.add('hidden'); // Add a class to hide it initially

// Add scroll event listener
window.addEventListener('scroll', function() {
    const scrollPosition = window.scrollY || window.pageYOffset; // Get scroll position

    // Check if the user has scrolled past the landing page content
    if (scrollPosition > landingPageContent.offsetHeight) {
        statementsSection.classList.remove('hidden'); // Make statements section visible
    } else {
        statementsSection.classList.add('hidden'); // Hide statements section if scrolled up
    }
});

