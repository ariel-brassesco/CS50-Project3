'use strict';

// Update the price of a cart item
function update_price_item(item, price){
    // Update the Cart and Item Price
    findParentElementByClass(item, "cart-item-footer").querySelector('.cart-item-price').innerHTML = parseFloat(price).toFixed(2);
}

// Update the total cart
function update_total_cart(total){
    // Update the Total Cost of Cart and Item Price
    document.getElementById('cart-total-cost').innerHTML = parseFloat(total).toFixed(2);
}

// Request a POST to update the quantity of a cart item
function update_item_quantity(item) {
    const btn_checkout = document.getElementById('cart-checkout-btn');
    // Initialize new request
    const request = new XMLHttpRequest();
    let post_url = window.location.origin + '/shopping/update_quantity/' + item.dataset.id;

    // Disabled checkout button
    btn_checkout.disabled = true;
    // Start request
    request.open('POST', post_url);

    // Callback function for when request completes
    request.onload = () => {
        // Extract JSON data from request
        const data = JSON.parse(request.responseText);
        // Print the status request in console
        if (data.success) {
            // Update the Total Cost of Cart and Item Price
            //update_price_item(index, data['price_item']);
            update_price_item(item, data['price_item']);
            update_total_cart(data['new_total']);
            console.log('Success quantity update');
        } else {
            console.log(data.error);
        }
        // Enabled checkout button
        btn_checkout.disabled = false;
    }

    // Add data to send with request
    const data = new FormData();
    data.append('quantity', item.value);
    // Send request
    request.send(data);

    return false;
}

// Show and hide the inputs for delivery
function show_hide_address_options(elem){
    const delivery_address = document.getElementsByClassName('cart-delivery-inputs')[0];
    // Show or hide the address options
    if (elem.value === 'T' && elem.checked) {
        delivery_address.classList.remove('expand');
    } 
    
    if (elem.value === 'D' && elem.checked) {
        delivery_address.classList.add('expand');
    }
    
}

// Show and hide the options for delivery (takeaway or delivery)
function show_hide_takeout_options(btn){
    const cart_takeout = document.getElementsByClassName('cart-delivery-options')[0];
    // Show or hide the takeout options
    cart_takeout.classList.toggle('expand');
    // Rotate the btn
    btn.classList.toggle('rotate-180');
}

// Sum a unit of quantity cart item
function item_quantity_plus(item){

    let quantity = parseInt(item.value, 10);
    if (isNaN(quantity)) {
        quantity = 1;
    } else {
        quantity += 1;
    }
    // Dispatch the event change on item
    item.value = quantity;
    let event = new Event('change', {bubbles: true});
    item.dispatchEvent(event);
}

// Less a unit of quantity cart item
function item_quantity_minus(item){
    let quantity = parseInt(item.value, 10);
    
    if (isNaN(quantity)) {
        quantity = 1;
    } else {
        quantity -= 1;
    }
    
    item.value = quantity;
    // Dispatch the event change on item
    let event = new Event('change', {bubbles: true});
    item.dispatchEvent(event);
}

// Set the queantity of a cart item and fix the range between 1-10 units
function item_quantity_set(item, func, ...args) {
    let quantity = parseInt(item.value, 10);
    
    // Check the value
    if (isNaN(quantity)) {
        item.value = 1;
    } else if (quantity > 10){
        item.value = 10;
    } else if (quantity < 1){
        item.value = 1;
    } else {
        item.value = quantity;
    }
    
    // Execute the callback function
    if (func){
        func(item, ...args);
    }
    
}

// Open the modal for edit a cart item
const item_editor_open = (id) => {
    const modal = document.getElementById('modal-cart-item-edit');
    const loader = modal.querySelector("div.loader");
    
    //Show the modal and loader
    show_modal(modal);
    run_loader_waiting(loader); 

    //Request the item data
    let post_url = window.location.origin + '/shopping/data_item/' + id;
    fetch(post_url,{
        method: 'POST',
        headers: {
            'X-CSRFToken': Cookies.get('csrftoken'),
        }
    }).then(res => res.json())
    .then(res => {
        if (res.success){
            //Hide the Loader
            run_loader_waiting(loader);
            //Add the content
            modal.querySelector(".product-form").innerHTML = res.page;
            //Update the size price
            const item = modal.querySelector('.cart-item-footer');
            update_product_sizes_price(item, null);
        }
    });
}

// Load events for the cart
function loadCart(){
    const btn_checkout = document.getElementById('cart-checkout');
    
    btn_checkout.addEventListener('submit', checkout_cart, false);
    
    document.addEventListener('click', (e)=> {
        // Add the event click to show and hide the takeout options
        if(e.target.id === 'cart-takeout-show'){
            show_hide_takeout_options(e.target);
        }
        // Add edit items in cart
        if(e.target.classList.contains('cart-item-edit')) {
            item_editor_open(e.target.dataset.id);
        }
    }, false)

    document.addEventListener('change', (e)=> {
        //Add events to check inputs options
        if (e.target.name === "deli-mode"){
            show_hide_address_options(e.target);
        }
    }, false);
}
