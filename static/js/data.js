'use strict';
// Functions to manage the localStorage
function getData(key) {
    if (!localStorage.getItem(key)) return false;
    return JSON.parse(localStorage.getItem(key));
}

function saveData(key, data) {
    try {
        localStorage.setItem(key, JSON.stringify(data));
        return true;
    }
    catch(error){
        console.log('An error was ocurred');
        return false;
    }
}

function getProductSizePrices(form_elem) {

    let product = form_elem['product'].value;
    let presentation = form_elem['presentation'].value;
    let prices = getData('products');

    return prices[product][presentation]
}

function getProductFormPrice(form_elem){
    let product = form_elem['product'].value;
    let size = (form_elem['size'])?form_elem['size'].value:null;
    let presentation = form_elem['presentation'].value;
    let additionals = form_elem.querySelectorAll('input[name="additionals"]:checked');
    let quantity = parseFloat(form_elem["item-quantity"].value);
    let prices = getData('products')[product];
    let product_price = 0.0

    // Sum the additionals
    for (let i=0; i < additionals.length; i++){
        let add_id = additionals[i].value;
        let price_add = parseFloat(prices['additionals'][add_id]);
        product_price += price_add;
    }
    //Return the price
    let price = (size)?prices[presentation][size]:prices[presentation];
    return product_price + quantity*price;
}

// Functions to find Elements in the DOM
function findParentElementByClass(e, cls) {
    if (e === document.body) return null;
    let parent = e.parentElement;
    return (parent.classList.contains(cls))?parent: findParentElementByClass(parent, cls);
}

function findParentElementByTagName(e, tag) {
    if (e === document.body) return null;
    let parent = e.parentElement;
    return (parent.nodeName == tag.toUpperCase())?parent: findParentElementByTagName(parent, tag);
}
