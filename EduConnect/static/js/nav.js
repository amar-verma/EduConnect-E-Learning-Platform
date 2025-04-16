
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
