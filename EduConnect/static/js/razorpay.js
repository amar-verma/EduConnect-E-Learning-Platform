var options = {
    "key": "rzp_test_Hh5tcDeBWtFzbE",  // Enter the Key ID from the Django backend
    "amount": "{{ sum }}",  // Amount in paise (1 INR = 100 paise)
    "currency": "INR",
    "name": "{{ student.first_name }}",
    "description": "Test Transaction",
    "image": "/static/img/clogo.png",
    "order_id": "{{ payment.id }}",  // Razorpay order ID from Django
    "handler": function (response) {

        var data = {
            payment_id: response.razorpay_payment_id,
            order_id: response.razorpay_order_id,
            signature: response.razorpay_signature,
            student_id: "{{ student.student_id }}",  // Passing student ID
            course_id: "{{ course.id }}"  // Passing course ID
        };

        $.ajax({
            type: 'POST',
            url: '/course/payment-success/',  // Django view handling the payment
            data: data,
            headers: {
                'X-CSRFToken': '{{ csrf_token }}'  // CSRF token for security
            },
            success: function (response) {
                if (response.status == 'success') {
                    window.location.href = "/course/payment-success/";  
                } else {
                    window.location.href = "/course/payment-success/";  // Redirect failure
                }
            },
            error: function () {
                // alert("Error occurred while processing the payment.");
            }
        });

    },
    "prefill": {
        "name": "{{ student.first_name }}",
        "email": "{{ student.user.email | default:'amarkumarverma2004@gmail.com' }}",
        "contact": "{{ student.phone_number }}"  // Remove quotes around variable
    },
    "notes": {
        "address": "EduConnect Razorpay Corporate Office"
    },
    "theme": {
        "color": "#3399cc"
    }
};

// Handle payment failure
var rzp1 = new Razorpay(options);
rzp1.on('payment.failed', function (response) {
    // alert("Payment failed: " + response.error.reason);

    var data = {
        payment_id: response.error.metadata.payment_id,
        order_id: response.error.metadata.order_id,
        student_id: "{{ student.id }}",
        course_id: "{{ course.id }}",
        status: "failed"
    };

    $.ajax({
        type: 'POST',
        url: '/course/payment-failure/',  // Separate endpoint for failed payments
        data: data,
        headers: {
            'X-CSRFToken': '{{ csrf_token }}'
        },
        success: function (response) {
            window.location.href = "/course/payment-success/";  
        },
        error: function () {
            // alert("Error occurred while processing the failed payment.");
        }
    });
});

// Open Razorpay modal on button click
document.getElementById('rzp-button1').onclick = function(e) {
    rzp1.open();
    e.preventDefault();
};
