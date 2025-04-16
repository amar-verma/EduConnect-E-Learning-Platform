let editor;

window.onload = function () {
    editor = ace.edit("editor");
    editor.setTheme("ace/theme/monokai");
    editor.session.setMode("ace/mode/c_cpp");
};

function changeLanguage() {
    let language = $('#language').val();
    if (language == 'c' || language == 'cpp') editor.session.setMode("ace/mode/c_cpp");
    else if (language == 'php') editor.session.setMode("ace/mode/php");
    else if (language == 'python') editor.session.setMode("ace/mode/python");
    else if (language == 'node') editor.session.setMode("ace/mode/javascript");
    else if (language == 'java') editor.session.setMode("ace/mode/java");
}
function submitCode() {
    // Assuming Ace Editor is used
    const editor = ace.edit("editor");
    const code = editor.getValue();
    document.getElementById("code").value = code;
}
// function executeCode() {
//     const url = "{% url 'submit_code' %}";  

//     $.ajax({
//         url: url,
//         method: "POST",
//         data: {
//             language: $("#language").val(),
//             code: editor.getSession().getValue()
//         },
//         headers: {
//             "X-CSRFToken": "{{ csrf_token }}"  // Include CSRF token for security
//         },
//         success: function (response) {
//             if (response.status === "success") {
//                 $(".output").text(response.output);
//             } else {
//                 $(".output").text("Error: " + response.message);
//             }
//         },
//         error: function (xhr, status, error) {
//             $(".output").text("AJAX error: " + error);
//         }
//     });
// }
