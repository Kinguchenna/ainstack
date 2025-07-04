
$(document).ready(function () {


    // $("#toSpeach").on("click", function (e) {
    //     e.preventDefault();
    //     var voicetext = $("#voicetext").val();
    //     var ShortName = $("#ShortName").val();
    //     var speed = $("#speed").val();
    //     var pitch = $("#pitch").val();
    //     // alert("sending");

    //     // Validate all fields
    //     if (!voicetext || !ShortName || !speed || !pitch) {
    //         errorMessage = "Please fill in all required fields.";
    //         displayError(errorMessage);
    //         $("#toSpeach").show();
    //         $(".spinner").hide();
    //         return;
    //     }
    //     // alert(speed);

    //     var button = $(this);
    //     // button.text("Processing...");
    //     button.disabled = false;
    //     $("#toSpeach").hide();
    //     $(".spinner").show();

    //     $.ajax({
    //         url: 'http://127.0.0.1:8000/tts/',
    //         type: 'GET',
    //         dataType: 'json',
    //         data: { pitch: pitch, speed: speed, text: voicetext, ShortName: ShortName },
    //         success: function (response) {
    //             if (response && response.voicetext == "") {
    //                 const errorMessage = "Text field and, or voice type cannot be empty.";
    //                 displayError(errorMessage);
    //                 button.prop("disabled", false);
    //                 // button.text("Convert to Speech");
    //                 $("#toSpeach").show();
    //                 $(".spinner").hide();
    //             } else {
    //                 button.prop("disabled", false);
    //                 // button.text("Convert to Speech");
    //                 // Set audio player source and show it
    //                 $("#toSpeach").show();
    //                 $(".spinner").hide();
    //                 $("#audioPlayer").attr("src", response.file_url).show();
    //                 // Set download link
    //                 $("#downloadLink").attr("href", response.file_url).show();
    //                 hideError();
    //             }
    //         },
    //         error: function (xhr, status, error) {
    //             const errorMessage = xhr.responseJSON?.message || "An unexpected error occurred. Please try again.";
    //             console.log("An error occurred: " + errorMessage);
    //             $("#toSpeach").show();
    //             $(".spinner").hide();
    //             // Enable the button and reset text
    //             button.prop("disabled", false);
    //             // button.text("Convert to Speech");

    //             // Show error in a div
    //             displayError(errorMessage);
    //         }
    //     });

    // });



    $("#toSpeach").on("click", function (e) {
        e.preventDefault();
        var voicetext = $("#voicetext").val();
        var ShortName = $("#ShortName").val();
        var speed = $("#speed").val();
        var pitch = $("#pitch").val();
    
        if (!voicetext || !ShortName || !speed || !pitch) {
            const errorMessage = "Please fill in all required fields.";
            displayError(errorMessage);
            $("#toSpeach").show();
            $(".spinner").hide();
            return;
        }
    
        var button = $(this);
        button.prop("disabled", true);
        $("#toSpeach").hide();
        $(".spinner").show();
    
        $.ajax({
            url: '/tts/',
            type: 'GET',
            dataType: 'json',
            data: { pitch: pitch, speed: speed, text: voicetext, ShortName: ShortName },
            success: function (response) {
                if (response && response.voicetext == "") {
                    const errorMessage = "Text field and/or voice type cannot be empty.";
                    displayError(errorMessage);
                    button.prop("disabled", false);
                    $("#toSpeach").show();
                    $(".spinner").hide();
                } else {
                    button.prop("disabled", false);
                    $("#toSpeach").show();
                    $(".spinner").hide();
                    $("#audioPlayer").attr("src", response.file_url).show();
                    $("#downloadLink").attr("href", response.file_url).show();
                    hideError();
                }
            },
            error: function (xhr, status, error) {
                let errorMessage = "An unexpected error occurred. Please try again.";
    
                if (xhr.responseJSON && xhr.responseJSON.message) {
                    errorMessage = xhr.responseJSON.message;
                    if (xhr.responseJSON.details) {
                        console.error("Details:", xhr.responseJSON.details);
                    }
                } else if (xhr.responseText) {
                    try {
                        let resp = JSON.parse(xhr.responseText);
                        if (resp.message) errorMessage = resp.message;
                    } catch {
                        errorMessage = xhr.responseText;
                    }
                }
    
                console.error("AJAX error:", errorMessage);
                $("#toSpeach").show();
                $(".spinner").hide();
                button.prop("disabled", false);
                displayError(errorMessage);
            }
        });
    });
    


    $("#sampleVoice").on("click", function (e) {
        e.preventDefault();
        var voicetext = $("#voicetext").val();
        var ShortName = $("#ShortName").val();
        var speed = $("#speed").val();
        var pitch = $("#pitch").val();

        // Validate all fields
        if (!voicetext || !ShortName || !speed || !pitch) {
            const errorBox = document.getElementById("errorBox"); // Make sure errorBox is defined
            errorBox.style.display = "block";
            errorBox.innerText = "Please fill in all required fields.";

            $("#toSpeach").show();
            $(".spinner").hide();
            return;
        }
        // alert(speed);

        var button = $(this);
        // button.text("Processing...");
        button.disabled = false;
        $("#toSpeach").hide();
        $(".spinner").show();

        $.ajax({
            url: '/tts/',
            type: 'GET',
            dataType: 'json',
            data: { pitch: pitch, speed: speed, text: voicetext, ShortName: ShortName },
            success: function (response) {
                if (response && response.voicetext == "") {
                    const errorMessage = "Text field and, or voice type cannot be empty.";
                    displayError(errorMessage);
                    button.prop("disabled", false);
                    // button.text("Convert to Speech");
                    $("#toSpeach").show();
                    $(".spinner").hide();
                } else {
                    button.prop("disabled", false);
                    // button.text("Convert to Speech");
                    // Set audio player source and show it
                    $("#toSpeach").show();
                    $(".spinner").hide();
                    $("#audioPlayer").attr("src", response.file_url).show();
                    // Set download link
                    // $("#downloadLink").attr("href", response.file_url).show();
                }
            },
            error: function (xhr, status, error) {
                const errorMessage = xhr.responseJSON?.message || "An unexpected error occurred. Please try again.";
                console.log("An error occurred: " + errorMessage);
                $("#toSpeach").show();
                $(".spinner").hide();
                // Enable the button and reset text
                button.prop("disabled", false);
                // button.text("Convert to Speech");

                // Show error in a div
                displayError(errorMessage);
            }
        });

    });



    $("#register-form").on("submit", function (e) {
        e.preventDefault();  // Prevent the form from submitting the traditional way
        // alert("hi");
        var username = $("#username").val();
        var email = $("#email").val();
        var password = $("#password").val();
        var password_confirm = $("#password_confirm").val();

        // Check if passwords match
        if (password !== password_confirm) {
            displayError("Passwords do not match.");
            return; // Stop further processing if passwords don't match
        }

        var button = $("#register");
        button.text("Registering...");
        button.prop("disabled", true);

        // Send the data via AJAX
        $.ajax({
            url: '/register-view/',  // URL for the registration view
            type: 'POST',
            dataType: 'json',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}'  // CSRF Token for Django protection
            },
            data: {
                'username': username,
                'email': email,
                'password': password,
                'password_confirm': password_confirm
            },
            success: function (response) {
                button.prop("disabled", false);
                button.text("Register");

                if (response.message === 'registered') {
                    // alert('Registration successful!');
                    // Redirect after registration, for example to login page
                    window.location.href = '/';
                    // window.location.href = '/login/';
                } else {
                    displayError(response.message);
                }
            },
            error: function (xhr, status, error) {
                button.prop("disabled", false);
                button.text("Register");

                let errMsg = "An error occurred: ";
                try {
                    const response = JSON.parse(xhr.responseText);
                    errMsg += response.message || error;
                } catch (e) {
                    errMsg += error;
                }

                displayError(errMsg);
            }

        });
    });

    // Function to display error messages
    // function displayError(message) {
    //     $(".error-message").text(message).show();
    // }


    function displayError(message) {
        const errorDiv = $("#error-message");
        errorDiv.html(message).show();
    }
    function hideError() {
        const errorDiv = $("#error-message");
        errorDiv.hide();
    }




    $("#login").on("click", function (e) {
        e.preventDefault();

        var username = $("#username").val();
        var password = $("#password").val();

        var csrf_token = $('input[name="csrfmiddlewaretoken"]').val();  // Get CSRF token from the hidden input field

        $.ajax({
            url: '/login/',  // Adjust the URL as needed
            type: 'POST',
            data: {
                'username': username,
                'password': password,
                'csrfmiddlewaretoken': csrf_token
            },
            success: function (response) {
                if (response.message === 'Login successful!') {
                    // Redirect after registration, for example to login page
                    window.location.href = '/';
                } else {
                    displayError(response.message);
                }
                // Redirect or update UI after successful login
            },
            error: function (xhr, status, error) {
                console.log("Error: ", error);
                alert("Login failed: " + xhr.responseJSON.message);
            }
        });
    });





});



// $(document).ready(function(){
//     $("#toSpeach").on("click", function(e){
//         e.preventDefault();
//         let btn = $(this);
//         btn.text("Processing...");
//         btn.prop("disabled", true);

//         $.ajax({
//             url: '/tts/',
//             type: 'GET',
//             data: {
//                 text: $('#voicetext').val(),
//                 ShortName: $('#sprachwahl').val()
//             },
//             success: function(response) {
//                 console.log("Success:", response);
//                 btn.text("Convert to Speech");
//                 btn.prop("disabled", false);
//             },
//             error: function(xhr, status, error) {
//                 console.log("Error:", error);
//                 btn.text("Convert to Speech");
//                 btn.prop("disabled", false);
//             }
//         });
//     });
// });
