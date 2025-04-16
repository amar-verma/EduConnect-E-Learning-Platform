
const viewMoreBtn = document.getElementById('viewMoreBtn');
const courseContent = document.getElementById('courseContent');

viewMoreBtn.addEventListener('click', () => {
  if (courseContent.classList.contains('show-less')) {
    courseContent.classList.remove('show-less');
    viewMoreBtn.textContent = "View less";
  } else {
    courseContent.classList.add('show-less');
    viewMoreBtn.textContent = "View More";
  }
});

document.addEventListener("DOMContentLoaded", function () {
  const btnLeft = document.getElementById("btn-left");
  const btnRight = document.getElementById("btn-right");
  const wrapper = document.querySelector(".swiper-wrapper");

  btnLeft.addEventListener("click", () => {
    wrapper.scrollBy({
      left: -200, // Adjust scroll amount based on card size
      behavior: "smooth",
    });
  });

  btnRight.addEventListener("click", () => {
    wrapper.scrollBy({
      left: 200, // Adjust scroll amount based on card size
      behavior: "smooth",
    });
  });
});