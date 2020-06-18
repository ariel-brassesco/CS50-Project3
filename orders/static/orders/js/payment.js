'use strict';
// Redirect to Stripe page to pay
function stripe_checkout(session_id){
    var stripe = Stripe('pk_test_Yqj2w9ax4qsL9fv6YS8CdCYU00ebyWvnZ4');
    
    stripe.redirectToCheckout({
        // Make the id field from the Checkout Session creation API response
        // available to this file, so you can provide it as parameter here
        // instead of the {{CHECKOUT_SESSION_ID}} placeholder.
        sessionId: session_id

    }).then(function (result) {
        // If `redirectToCheckout` fails due to a browser or network
        // error, display the localized error message to your customer
        // using `result.error.message`.
        console.log(result);
        console.log(result.error.message);
    });
}

function checkout_cart(e) {
    e.preventDefault();
    //Show loader
    const loader = document.getElementById('loader-checkout');
    show_modal(loader);

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
            console.log('Purchase Success');
            stripe_checkout(data.session);
        } else {
            close_modal(loader);
            console.log((data.error)?data.error: data['request-error']);
        }
    }

    // Add data to send with request
    const data = new FormData(this);
    // Send request
    request.send(data);

    return false;
}

