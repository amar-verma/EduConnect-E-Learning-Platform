
    document.addEventListener("DOMContentLoaded", function () {
    const filters = ["category","sortBy", "price", "enrollment", "rating", "popularity"];

    // Trigger filters on initial load
    applyFilters();

    filters.forEach(filter => {
        document.getElementById(filter).addEventListener("change", applyFilters);
    });

    function applyFilters() {
        const category = document.getElementById("category").value;
        const sortBy = document.getElementById("sortBy").value;
        const price = document.getElementById("price").value;
        const enrollment = document.getElementById("enrollment").value;
        const rating = document.getElementById("rating").value;
        const popularity = document.getElementById("popularity").value;

        fetch(`/filter_courses/?category=${category}&sortBy=${sortBy}&price=${price}&enrollment=${enrollment}&rating=${rating}&popularity=${popularity}`)
        .then(response => response.json())
        .then(data => updateCourses(data.courses))
        .catch(error => console.error("Error fetching filtered data:", error));
    }
    

    function updateCourses(courses) {
        const container = document.querySelector(".card-flow");
        container.innerHTML = ""; // Clear current courses

        courses.forEach(course => {
          let ratingDisplay;
          let iconlike =`<i class="bi bi-hand-thumbs-up-fill text-primary"></i> `
          let iconcal =`<i class="bi bi-calendar-week text-success"></i> `
          
          // Check multiple conditions on course.rating
          if (course.rating === 5) {
              ratingDisplay = `<span class="text-warning"><i class="bi bi-star-fill"></i> <i class="bi bi-star-fill"></i> <i class="bi bi-star-fill"></i> <i class="bi bi-star-fill"></i> <i class="bi bi-star-fill"></i></span>`;
          } else if (course.rating === 4) {
              ratingDisplay = `<span class="text-warning"><i class="bi bi-star-fill"></i> <i class="bi bi-star-fill"></i> <i class="bi bi-star-fill"></i> <i class="bi bi-star-fill"></i> <i class="bi bi-star"></i></span>`;
          } else if (course.rating === 3) {
              ratingDisplay = `<span class="text-warning"><i class="bi bi-star-fill"></i> <i class="bi bi-star-fill"></i> <i class="bi bi-star-fill"></i> <i class="bi bi-star"></i> <i class="bi bi-star"></i></span>`;
          } else if (course.rating === 2) {
              ratingDisplay = `<span class="text-warning"><i class="bi bi-star-fill"></i> <i class="bi bi-star-fill"></i> <i class="bi bi-star"></i> <i class="bi bi-star"></i> <i class="bi bi-star"></i></span>`;
          } else if (course.rating === 1) {
              ratingDisplay = `<span class="text-warning"><i class="bi bi-star-fill"></i> <i class="bi bi-star"></i> <i class="bi bi-star"></i> <i class="bi bi-star"></i> <i class="bi bi-star"></i></span>`;
          } else {
              ratingDisplay = `<span class="text-warning"><i class="bi bi-star"></i> <i class="bi bi-star"></i> <i class="bi bi-star"></i> <i class="bi bi-star"></i> <i class="bi bi-star"></i></span>`;
          }
          // const createdDate = new Date(course.created_at).toISOString().split('T')[0];

            const card = `
                <div class="col-md-3 card-flow-wdth mb-1">
                  <a class='text-decoration-none text-black' href="${course.detail_url}">
                    <div class="card custom-card edu-card1">
                        <img src="${course.course_img}" class="card-img-top" alt="${course.title}">
                        <div class="card-body">
                            <div class="title-space">
                            <h5 class="card-title">${course.title}</h5>
                            </div>
                            <p class="duration"><i class="fa fa-calendar"></i>
                               ${ratingDisplay} 
                            </p>
                            <p class="likes "><span class="me-2">${iconlike} ${course.like}</span>  ${iconcal} ${course.created_at} </p>
                            <p class="price m-0">Price: ₹${course.price}</p>
                            <p class="enrollment ">Enrolled: ${course.enroll}/${course.max_enrollments}</p>
                            
                        </div>
                    </div>
                  </a>
                </div>`;
            container.insertAdjacentHTML("beforeend", card);
        });
    }
});

