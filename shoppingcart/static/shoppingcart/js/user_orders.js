'use strict';
// Request the status for orders
const statusOrders = (url, method) => {
    return fetch(url, {
        method: method,
    }).then(res => res.json());  
}

// Create the status bars for order users
// and return the DOM element
const createStaBarElements = (status) => {
    //Create a DocumentFragment
    const fragment = new DocumentFragment();
    const container = document.createElement('div');

    container.classList.add('status-container');
    //Create the status bar elements
    for (let i=0; i < status.length; i++){
        let stBar =  document.createElement('span');
        stBar.setAttribute('data-value', status[i][0]);
        stBar.setAttribute('data-state', `status-${status[i][1].toLowerCase()}`);
        stBar.classList.add('status-bar');
        container.appendChild(stBar);
    }
    //Create and append the final status bar
    let finalStaBar =  document.createElement('span');
    finalStaBar.classList.add('status-bar-final', 'inactive');
    container.appendChild(finalStaBar);
    
    fragment.appendChild(container);
    return fragment;
}

// Asign the status bar for each order
const asignStatusBar = (elem, readyStatus) => {
    const orderSta = elem.dataset.status;
    const staBars = elem.querySelectorAll('.status-bar');
    
    if (orderSta == readyStatus) {
        Array.from(staBars).forEach(bar =>  bar.classList.add('inactive'));
        elem.querySelector('.status-bar-final').classList.replace('inactive', 'status-ready');
    } else {

        Array.from(staBars).forEach(bar =>{
            if (bar.dataset.value <= orderSta) bar.classList.add(bar.dataset.state,'status-complete');
            if (bar.dataset.value == orderSta) bar.classList.add('status-incomplete');
        })
    }
}

document.addEventListener('DOMContentLoaded', () => {
    
    const divOrders = document.getElementsByClassName('order-user-status');
    const post_url = window.location.origin + '/shopping/api/get-order-status';
    
    statusOrders(post_url, 'GET')
        .then(data => {
            const nst = data.status.length;
            const finalSta = data.status[nst-1][0];
            //Add the status bar element in div
            Array.from(divOrders).forEach(elem => {
                elem.appendChild(createStaBarElements(data.status));
                //Use setTimeout to see the transitions
                setTimeout(() => asignStatusBar(elem, finalSta), 100);
            });
            
        }).catch(console.error);



});