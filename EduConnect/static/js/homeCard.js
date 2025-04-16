const slides = document.querySelectorAll('.slide');
const prevButton = document.getElementById('prev');
const nextButton = document.getElementById('next');
let currentSlide = 0;

function updateSlides() {
  slides.forEach((slide, index) => {
    slide.classList.toggle('active', index === currentSlide);
  });
}

prevButton.addEventListener('click', () => {
  currentSlide = (currentSlide - 1 + slides.length) % slides.length;
  updateSlides();
});

nextButton.addEventListener('click', () => {
  currentSlide = (currentSlide + 1) % slides.length;
  updateSlides();
});


// ......

// Get the elements
const mstPopularDiv = document.getElementById('mst-popular');
const bestCoursesDiv = document.getElementById('best-courses');
const mostPopularLink = document.getElementById('most-popular-link');
const bestCoursesLink = document.getElementById('best-courses-link');
const activeBar = document.querySelector('.active-bar');

// Add event listeners for the links
mostPopularLink.addEventListener('click', function () {
  mstPopularDiv.style.display = 'block'; // Show the Most Popular div
  bestCoursesDiv.style.display = 'none'; // Hide the Best Courses div
  mostPopularLink.style.color = 'blue';
  bestCoursesLink.style.color = 'black';
  activeBar.style.transform = 'translateX(0%)'; // Move active bar to Most Popular
});

bestCoursesLink.addEventListener('click', function () {
  mstPopularDiv.style.display = 'none'; // Hide the Most Popular div
  bestCoursesDiv.style.display = 'block'; // Show the Best Courses div
  mostPopularLink.style.color = 'black';
  bestCoursesLink.style.color = 'blue';
  activeBar.style.transform = 'translateX(100%)'; // Move active bar to Best Courses
});


document.addEventListener("DOMContentLoaded", function () {
  const textElement = document.getElementById("edu-connect-text");
  const button = document.getElementById("read-more-btn");
  const fullText = textElement.innerHTML; // Store the full text
  const maxLength = 350; // Character limit

  if (fullText.length > maxLength) {
    const truncatedText = fullText.substring(0, maxLength) + "...";
    textElement.innerHTML = truncatedText;

    let isExpanded = false; // Track the state of the text

    button.addEventListener("click", function () {
      if (isExpanded) {
        textElement.innerHTML = truncatedText;
        button.innerText = "Read More";
      } else {
        textElement.innerHTML = fullText;
        button.innerText = "Read Less";
      }
      isExpanded = !isExpanded;
    });
  } else {
    button.style.display = "none"; // Hide button if text is short
  }
});