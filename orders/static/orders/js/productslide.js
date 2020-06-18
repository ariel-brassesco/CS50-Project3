'use strict';
// Next/previous controls
function changeSlides(index, n) {
  let slide = index + n;
  return showSlides(slide);
}

// Thumbnail image controls
function currentSlide(slide) {
  return showSlides(slide);
}

// Change the Slide and show it. Reset the values
function showSlides(n) {
  let slides = document.getElementsByClassName("product-slide");
  let index = n;
  if (n > slides.length) {index = 1}
  if (n < 1) {index = slides.length}
  
  for (let i = 0; i < slides.length; i++) {
    slides[i].classList.add('inactive'); 
  }
  
  slides[index-1].classList.remove('inactive');
  reset_form_product(index-1);
  return index;
}

function loadProductClick(){
    const modal = document.getElementById("modal-products");
    let slideIndex = 1;
    
    document.addEventListener('click', (e) => {
      // Next and Previous slide
      if (e.target.id === 'next-product') slideIndex = changeSlides(slideIndex, 1);
      if (e.target.id === 'prev-product') slideIndex = changeSlides(slideIndex, -1);

      // Show the slider when click in any product
      const parent = findParentElementByClass(e.target, 'profile-card-product');
      if (parent) {
        let slide = parseInt(parent.dataset.indexslide);
        
        show_modal(modal);
        slideIndex = currentSlide(slide);
      }

    }, false);
}
