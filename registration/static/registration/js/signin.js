'use strict';

// Validate the password
function validate_password(elem, btn, ev){

    if (elem.value == ev.target.value) {
        btn.disabled = false;
    } else {
        btn.disabled = true;
    }
}

// Submit the sign in form
function signin_form(e){
    e.preventDefault();
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
            console.log('Signin User Success');
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
function show_message_error(messages){
    let message_modal = document.getElementsByClassName('msg')[0];

    for (let i=0 ; i < messages.length; i++) {
        let msg = document.createElement('p');
        msg.classList.add('error-msg');
        msg.innerHTML = messages[i];
        message_modal.appendChild(msg);
    }

    message_modal.classList.toggle('inactive');
    message_modal.classList.toggle('error');
    setTimeout(function(){
        message_modal.classList.toggle('inactive');
    }, 4000);
}

document.addEventListener('DOMContentLoaded', () => {
    var pass1 = document.getElementsByName('password')[0];
    var pass2 = document.getElementsByName('pass-check')[0];
    var btn = document.getElementsByTagName('button')[0];
    const signin_btn = document.getElementById('signin-form');
    
    // Disable the submit button
    btn.disabled = true;
    pass2.addEventListener('input', validate_password.bind(null, pass1, btn), false);   

    //Submit signin Form
    signin_btn.addEventListener('submit', signin_form, false);
});