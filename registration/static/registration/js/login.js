'use strict';

// Submit login form
function login_form(e){
    e.preventDefault();
    if (this.password.value === "" || this.username.value === "") {
        return false;
    }
    // Initialize new request
    const request = new XMLHttpRequest();
    
    request.open(this.method, this.action);

    // Callback function for when request completes
    request.onload = () => {
        // Extract JSON data from request
        const data = JSON.parse(request.responseText);
        
        // Update the result div
        if (data.success) {
            // Save the user data in localStore
            console.log('Login Success');
            location.replace(data.redirect);
        } else {
            console.log(data.error);
            show_message_error(data.message);
        }
    }

    // Add data to send with request
    const data = new FormData(this);
    // Send request
    request.send(data);

    return false;
}

// Show error messages from submit form
function show_message_error(message){
    const message_error = document.querySelector("spam.error-msg");

    message_error.innerHTML = message;
}

document.addEventListener('DOMContentLoaded', () => {
    const login_btn = document.getElementById('login-form');

    //Submit signin Form
    login_btn.addEventListener('submit', login_form, false);
});

