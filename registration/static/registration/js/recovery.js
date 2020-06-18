'use strict';

// Validate password for recovery password form
function validate_password(elem, btn, ev){

    if (elem.value == ev.target.value) {
        btn.disabled = false;
    } else {
        btn.disabled = true;
    }
}

// Submit recovery password form
function recovery_form(e){
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
            console.log('Change Password Success');
            location.replace(data.redirect);
        } else {
            console.log(data.error);
            if (data.error === 'username') {
                location.replace(data.redirect);
            }
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
    const message_error = document.querySelector(".list-error-msg");
    let list_error = document.createElement('ul');

    //Clear the content of message_error
    message_error.innerHTML = ""
    
    // Create the list of error messages
    for (let i=0; i < messages.length; i++){
        let msg = document.createElement('li');
        msg.innerHTML = messages[i];
        list_error.appendChild(msg);
    }

    //Insert the list error in message_error
    message_error.appendChild(list_error);
}

document.addEventListener('DOMContentLoaded', () => {
    let pass1 = document.getElementsByName('password')[0];
    let pass2 = document.getElementsByName('pass-check')[0];
    let btn = document.getElementsByTagName('button')[0];
    const recovery_btn = document.getElementById('recovery-form');
    
    // Disable the submit button
    if (btn) {
        btn.disabled = true;
        pass2.addEventListener('input', validate_password.bind(null, pass1, btn), false);   

        //Submit signin Form
        recovery_btn.addEventListener('submit', recovery_form, false);
    }
});