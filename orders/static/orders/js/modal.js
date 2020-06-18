'use strict';
// Show the modal, toggle the inactive class
function show_modal(modal) {
  modal.classList.toggle('inactive');
}
// Close the modal, toggle the inactive class
function close_modal(modal) {
  modal.classList.toggle('inactive');
}

// Update the prices of products by sizes in the DOM
function update_product_sizes_price(item, index){
  let form_product;
  
  if (item === null){
    form_product = document.getElementsByClassName('product-form')[index].getElementsByTagName('form')[0];
  } else {
    form_product = findParentElementByClass(item, 'product-form').getElementsByTagName('form')[0];
  }
  
  let spam_prices = form_product.getElementsByClassName('product-size-price');
  let prices = getProductSizePrices(form_product);

  for (let i=0; i < spam_prices.length; i++) {
    let size = form_product['size'][i].value;
    spam_prices[i].innerHTML = parseFloat(prices[size]).toFixed(2);
  }

  //Update the total price
  if (item === null) {
    update_form_product_price(form_product);
  } else {
    update_form_product_price(item);
  }
}

// Update the total price of item in the DOM
function update_form_product_price(item){
  const form_product = findParentElementByClass(item, 'product-form').getElementsByTagName('form')[0];
  let spam_price = form_product.getElementsByClassName("product-form-price")[0];
  let price = getProductFormPrice(form_product);

  spam_price.innerHTML = price.toFixed(2);
}

//Check if the additionals choosed are les than the maximun
function check_additionals(form_elem){
  const additionals = form_elem.querySelectorAll('input[name="additionals"]');
  var chooses = form_elem.querySelectorAll('input[name="additionals"]:checked');
  let product = form_elem['product'].value;
  let max_add = parseInt(getData('products')[product]['additionals']['max'], 10);
  
  if (max_add > 0) {
    if (chooses.length >= max_add) {
      for (let i=0; i < additionals.length; i++){
        if (!additionals[i].checked) {
          additionals[i].disabled = true;
        }
      }
    } else {
      for (let i=0; i < additionals.length; i++){
          additionals[i].disabled = false;
      }
    }
  }
  
  return chooses.length;
}

// Reset the from inputs and values
function reset_form_product(index){
  const product_form = document.querySelectorAll(".product-form form")[index];
  product_form['reset'].click();
  update_product_sizes_price(null,index);
}

const run_loader = (elem) => {
  //Run the animation in elem
  elem.classList.toggle('inactive');
}

const run_loader_success = (elem) => {
    //Run the animation in elem
    elem.classList.add('appearce');
    elem.querySelector("i").classList.add('ok-item');  
    
    //When the animation end, reload the page
    elem.querySelector("i").addEventListener('webkitAnimationEnd', ()=> {
      location.reload()
    });
    elem.querySelector("i").addEventListener('animationend', ()=> {
      location.reload()
    });
}

function add_item_to_cart(form) {
  
  // Disable button Add Item
  const btn_submit = form.querySelector('button[type="submit"]');
  btn_submit.disabled = true;
  // Run the Loader Waiting
  const loader_waiting = form.getElementsByClassName('waiting-loader')[0];
  run_loader(loader_waiting);

  // Initialize new request
  const request = new XMLHttpRequest();
  
  request.open(form.method, form.action);

  // Callback function for when request completes
  request.onload = () => {
      // Extract JSON data from request
      const data = JSON.parse(request.responseText);
      
      // Update the result div
      if (data.success) {
        console.log('Item Add Success.');  
        // Save the user data in localStore
        const loader_success = form.getElementsByClassName('success-loader')[0];
        run_loader_success(loader_success)
      } else {
          run_loader(loader_waiting);
          console.error(data.error);
      }
  }

  // Add data to send with request
  const data = new FormData(form);
  // Send request
  request.send(data);

  return false;
}

const edit_item_in_cart = (form) => {

  const data = new FormData(form);
  // Disable button Add Item
  const btn_submit = form.querySelector('button[type="submit"]');
  btn_submit.disabled = true;
  // Run the Loader Waiting
  const loader_waiting = form.getElementsByClassName('waiting-loader')[0];
  run_loader(loader_waiting);

  fetch(form.action,{
    method: 'POST',
    body: data,
    headers: {
        'X-CSRFToken': Cookies.get('csrftoken'),
    }
  }).then(res => res.json())
  .then(res => {
    if (res.success){
      console.log('Item Edit Success.');  
      // Save the user data in localStore
      const loader_success = form.getElementsByClassName('success-loader')[0];
      run_loader_success(loader_success);
    } else {
      run_loader(loader_waiting);
      console.error(res.error);
    }
  }).catch(console.error);
}

function loadModalEvents(){
  // Get the modal cart edit items
  const modal_user_cart = document.getElementById("modal-cart-item-edit");
  // Get the modal products
  const modal_products = document.getElementById("modal-products");
  
  document.addEventListener('click', (e)=>{
    // When the user clicks on <span> (x), close the modal
    if(e.target.id === 'close-modal-products'){
      close_modal(modal_products);
    }
    if(e.target.id === 'close-modal-edit-item'){
      close_modal(modal_user_cart);
      //Remove the content added
      let child = modal_user_cart.querySelector('.modal-content').lastChild;
      modal_user_cart.querySelector('.modal-content').removeChild(child);
    }

    //When click the minus button to quantity
    if (e.target.classList.contains('btn-minus')){
      const item = findParentElementByClass(e.target, 'cart-item-footer').querySelector('input[name="item-quantity"]');
      item_quantity_minus(item)
    }

    //When click the plus button to quantity
    if (e.target.classList.contains('btn-plus')){
      const item = findParentElementByClass(e.target, 'cart-item-footer').querySelector('input[name="item-quantity"]');
      item_quantity_plus(item);
    }

    //When click in swicht presentation
    //Switch the variations
    if (e.target.name === 'presentation'){
      //A variable for record previous value
      const parent = findParentElementByClass(e.target, 'product-presentations');
      const default_value = parent.dataset.default;
      let previous_value = parent.dataset.previous;
      
      if (e.target.value === previous_value){
        e.target.checked = false;
        parent.querySelector(`input[value="${default_value}"]`).checked = true;
        parent.dataset.previous = default_value;
      } else {
        parent.dataset.previous = e.target.value;
      }
      // Update the prices for the variation choice
      update_product_sizes_price(parent, null);
    }

    // Update when choose a size
    if (e.target.name === 'size'){
      update_form_product_price(e.target);
    }

    // Update when choose a topping
    if (e.target.name === 'additionals') {
      const parent_form = findParentElementByClass(e.target, 'product-form').querySelector('form');
      check_additionals(parent_form);
      update_form_product_price(e.target, null);
    }

  }, false);

  document.addEventListener('change', (e)=>{
    //When modify the quantity
    if(e.target.name === "item-quantity"){
      if (e.target.classList.contains('user-cart-item-quantity')){
        item_quantity_set(e.target, update_form_product_price);
      } 
      
      if (e.target.classList.contains('product-edit-item-quantity')){
        item_quantity_set(e.target, update_form_product_price);
      }

      if (e.target.classList.contains('card-edit-item-quantity')){
        item_quantity_set(e.target, update_item_quantity);
      }
    }
    
  }, false);

  document.addEventListener('submit', (e)=> {
    e.preventDefault();
    //Add product to cart
    if(e.target.dataset.type === 'add'){
      add_item_to_cart(e.target);
    }

    //Modify an item in the cart
    if(e.target.dataset.type === 'edit'){
      console.log(e.target);
      edit_item_in_cart(e.target);
    }

  }, false);

  // When the user clicks anywhere outside of the modal, close it
  window.addEventListener('click', (e)=> {
    if (e.target == modal_products) {
      close_modal(modal_products);
    }
    if (e.target == modal_user_cart) {
      close_modal(modal_user_cart);
      //Remove the content added
      let child = modal_user_cart.querySelector('.modal-content').lastChild;
      modal_user_cart.querySelector('.modal-content').removeChild(child);
    }

  }, false);
}
