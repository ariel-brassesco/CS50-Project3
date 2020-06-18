"use strict";
// Change the position of moving element according to the scroll
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

// Call the scroll event
const moveNavigation = (moveElem, fixedElem) => {
    let scrolling = false;
    window.addEventListener('scroll', (e) => {
        if(!scrolling){
            window.requestAnimationFrame(() => {
                scrollNav(moveElem, fixedElem);
                scrolling = false;
            });
        }
        scrolling = true;        
    }, false);
}

document.addEventListener("DOMContentLoaded", ()=>{
    
    const grid_nav = document.querySelector('.grid-nav');
    const nav_bar = document.querySelector('.index-about');
    const mql = matchMedia('(max-width: 600px)');

    // When resize the browser allow navigation bar moving with scroll
    // if the width of viewport is grater than 600px
    moveNavigation(nav_bar, grid_nav);
    
    window.addEventListener('resize', () => {
        if (!mql.matches) moveNavigation(nav_bar, grid_nav);
    }, false);
    
}, false);

