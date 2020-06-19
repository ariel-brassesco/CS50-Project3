'use strict';

//Request the data of products and save in localStorage
function getProductsData(){
    // Initialize new request
    const request = new XMLHttpRequest();
    
    request.open('POST', 'api/products');

    // Callback function for when request completes
    request.onload = () => {
        // Extract JSON data from request
        const data = JSON.parse(request.responseText);
        
        if (data.success) {
            // Save the products data in localStore
            console.log('Product Data Request Success.');
            saveData('products', data.products);
        } else {
            console.log(data.error);
        }
    }

    // Add data to send with request
    const data = new FormData();
    data.append('csrfmiddlewaretoken', Cookies.get('csrftoken'))
    // Send request
    request.send(data);

    return false;
}

// Move down the moveElem when scroll, using fixedElem as reference.
// The moveElem had to be in position relative or absolute
const scrollNav = (moveElem, fixedElem)=>{
        let dim_fixedElem = fixedElem.getBoundingClientRect();
        let dim_moveElem = moveElem.getBoundingClientRect();

        if (dim_fixedElem.bottom <= dim_moveElem.height){
            let margin = window.getComputedStyle(moveElem).marginTop;
            margin = parseInt(margin.replace("px",""));
            moveElem.style.top = (dim_fixedElem.height - dim_moveElem.height - 2*margin) + "px";
        } else if (dim_fixedElem.y <= 0) {
            moveElem.style.top = Math.abs(dim_fixedElem.y) + "px";
        } else {
            moveElem.style.top = "0px";
        }
}

// Generate a moving nav-bar. When you release, 
//the bar goes to the near border, left or right
const loadFixedNavBar = ()=>{
    const nav_bar = document.querySelector('.nav-bar-fixed');
    const move_bar = document.getElementById('move-nav-bar');
    const dim_move_bar = move_bar.getBoundingClientRect();
    
    // When press the mouse button
    document.addEventListener('mousedown', (e)=>{
        if (e.target.id === move_bar.id){
            move_bar.classList.replace('staying', 'moving');
            nav_bar.classList.remove('go-to-border');
        }
    }, false);
    // When stop pressing the mouse button
    document.addEventListener('mouseup', (e)=>{
        if (e.target.id === move_bar.id){
            move_bar.classList.replace('moving', 'staying');
            nav_bar.classList.add('go-to-border');
            
            let pos = (window.innerWidth/2 < e.clientX)?window.innerWidth-dim_move_bar.width-30:5;
            nav_bar.style.left = pos + 'px';
        }
    }, false);
    // When move the mouse
    document.addEventListener('mousemove', (e)=>{
        if (move_bar.classList.contains('moving')){
            nav_bar.style.top = e.clientY - dim_move_bar.height/2 + 'px';
            nav_bar.style.left = e.clientX - dim_move_bar.width/2 + 'px';
        }
    }, false);

    //Now the same above but for touch screen
    // When touch the nav bar to start moving
    document.addEventListener('touchstart', (e)=>{
        console.log(e.target);
        if (e.target.id === move_bar.id){
            move_bar.classList.replace('staying', 'moving');
            nav_bar.classList.remove('go-to-border');
        }
    }, false);
    // When stop touching the screen
    document.addEventListener('touchend', (e)=>{
        if (e.target.id === move_bar.id){
            move_bar.classList.replace('moving', 'staying');
            nav_bar.classList.add('go-to-border');
            
            let pos = (window.innerWidth/2 < e.changedTouches[0].clientX)?window.innerWidth-dim_move_bar.width-30:5;
            nav_bar.style.left = pos + 'px';
        }
    }, false);
    // When move the finger over the screen
    document.addEventListener('touchmove', (e)=>{
        if (move_bar.classList.contains('moving')){
            nav_bar.style.top = e.changedTouches[0].clientY - dim_move_bar.height/2 + 'px';
            nav_bar.style.left = e.changedTouches[0].clientX - dim_move_bar.width/2 + 'px';
        }
    }, false);
}

document.addEventListener('DOMContentLoaded', () => {
    const grid_nav = document.querySelector('.grid-nav');
    const cart = document.querySelector('#cart');
    
    getProductsData(); //Function in this file
    loadProductClick(); //Load Events in productslide.js
    loadCart(); //Load Events in shoppingcart/js/shopping_cart.js
    loadModalEvents(); //Load Events in modal.js
    loadFixedNavBar(); //Function in this file

    // Move the navigation bar when scroll
    let scrolling = false;
    window.addEventListener('scroll', (e) => {
        if(!scrolling){
            window.requestAnimationFrame(() => {
                scrollNav(cart, grid_nav);
                scrolling = false;
            })
        }
        scrolling = true;
        
    }, false);
    
});