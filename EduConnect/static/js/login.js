// Bootstrap validation script
(function () {
    'use strict';
    // Fetch all forms with the 'needs-validation' class
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(function (form) {
      form.addEventListener(
        'submit',
        function (event) {
          // Prevent submission if the form is invalid
          if (!form.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();
          }
          // Add Bootstrap validation styles
          form.classList.add('was-validated');
        },
        false
      );
    });
  })();



