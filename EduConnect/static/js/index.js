window.addEventListener("load", () => {
    const preloader = document.getElementById("preloader");
    preloader.style.opacity = "0";
    setTimeout(() => preloader.style.display = "none", 500); 
  });



      // JavaScript to toggle active content
      const menuItems = document.querySelectorAll('.menu-item');
      const contentItems = document.querySelectorAll('.content-item');
  
      menuItems.forEach(item => {
        item.addEventListener('mouseover', () => {
          // Remove active classes
          menuItems.forEach(i => i.classList.remove('active'));
          contentItems.forEach(i => i.classList.remove('active'));
  
          // Add active classes
          item.classList.add('active');
          const target = document.getElementById(item.dataset.target);
          target.classList.add('active');
        });
      });
