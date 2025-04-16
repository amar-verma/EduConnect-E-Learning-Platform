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