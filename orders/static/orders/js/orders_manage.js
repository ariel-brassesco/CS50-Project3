'use strict';

//Create a Loader for status
const createLoaderStatus = () => {
    const loader = document.createElement('span');
    loader.classList.add('status-loader');
    loader.textContent = 'LOADING';
    return loader;
}

//Change the status order
function changeOrderStatus(elem, prevStatus, newStatus){
    //Get status_options
    let status_options = getData('status_options');
    
    //Change the class and innerHTML
    elem.classList.remove(status_options[prevStatus-1].toLowerCase());
    elem.classList.add(status_options[newStatus-1].toLowerCase());
    elem.innerHTML = status_options[newStatus-1];
}

//Request and order status request
function changeOrderStatusRequest(order, elem){
    // Initialize new request
    const url = window.location.origin + '/shopping/api/chage-status';
    const data = new FormData();
    data.append('order', order);
    const loader = createLoaderStatus();
    const statusElem = elem.cloneNode(true);
    
    elem.parentNode.replaceChild(loader, elem);
    
    fetch(url,{
        method: 'POST',
        body: data,
        headers: {
            'X-CSRFToken': Cookies.get('csrftoken'),
        }
    }).then(res => res.json())
    .then(data => {            
        if (data.success){
            console.log('Change Status Order Request Success.');
            let prev_status = parseInt(data['prev_status']);
            let new_status = parseInt(data['new_status']);
            loader.parentNode.replaceChild(statusElem, loader);
            changeOrderStatus(statusElem, prev_status, new_status);

        } else {
            loader.parentNode.replaceChild(statusElem, loader);
            console.error(data.error);
            console.log(data.message);
        }
    }).catch(console.error);

    return false;
}

//Request the data for table
function requestData(filters={}){
    // Initialize new request
    const url = window.location.origin + '/shopping/api/orders';
    const data = new FormData();
    data.append('filters', JSON.stringify(filters));

    fetch(url,{
        method: 'POST',
        body: data,
        headers: {
            'X-CSRFToken': Cookies.get('csrftoken'),
        }
    }).then(res => res.json())
    .then(data => {  
        if (data.success){
            console.log('Orders Data Request Success.');
            // Save the orders data in localStore
            saveData('status_options', data.status_options);
            saveData('columns', data.columns);
            
            //Convert Datetime
            data.orders.map(function(time) {
                time['date'] = new Date(time['date']);
                return time;
            })

            // Ordering the data by date
            data.orders = orderDataBy(data.orders,'date', false);
            
            createPagination(data.orders.length, 20);
            createTable(data.orders);

        } else {
            console.error(data.error);
        }
    }).catch(console.error);
    
    return false;
}

//Create the table form data and show
function createTable(data){
    const table = document.getElementById('orders-table');
    const tableContent = document.createDocumentFragment();
    let cols = getData('columns');
    //let nrows = data.length;

    deleteTableContent(table);

    data.forEach(rowData => {
        let row = document.createElement('tr');
        for(let col of cols) {
            let cell = document.createElement('td');
            switch(col){
                case 'total':
                    //Set two decimal
                    cell.textContent = `$  ${rowData[col].toFixed(2)}`;
                    break;
                
                case 'order': 
                    // Create the link to Orders
                    let link = rowData['order_link'];
                    let order_number = rowData[col];
                    let a = create_link(link, order_number);
                    cell.append(a);
                    break;

                case 'date':
                    //Print the Date in Locale Format
                    cell.textContent = rowData[col].toLocaleString();
                    break;
                
                case 'status':
                    let status = create_status(rowData[col]);
                    cell.append(status);
                    break;
                
                default:
                    cell.textContent = rowData[col];
                    break;
            }
            row.appendChild(cell);
        }
        tableContent.appendChild(row);
    })
    
    //Add the tableContent Fragment to Table Body
    table.tBodies[0].append(tableContent);

    //Show the table
    showTable(table, 1);

    //Return the link to Order Number
    function create_link(link, number) {
        let a = document.createElement('a');
        
        a.setAttribute('href', link);
        a.setAttribute('target', 'blank');
        a.innerHTML = `# ${number.toString().padStart(5, '0')}`;

        return a;
    }
    //Return a span element to status order
    function create_status(status) {
        let elem = document.createElement('span');
        elem.classList.add(status.toLowerCase(), 'status-order');
        elem.textContent = status.toUpperCase();

        return elem;
    }
}

//Delete the content of table body to avoid render 
// the same data several times
function deleteTableContent(table){
    table.tBodies[0].textContent = '';
}

//Get the data form table and return
function getDataFromTable(table){
    const dataTable = [];
    const cols = getData('columns');
    const rows = Array.from(table.rows).slice(1);
    
    rows.forEach(rowData => {
        let dataRow = {};
        
        for (let col in cols) {
            let data = rowData.cells;
            switch(cols[col]){
                case 'total':
                    let total = parseFloat(data[col].innerHTML.slice(1));
                    dataRow[cols[col]] = total;
                    break;
                case 'order': 
                    let value = parseInt(data[col].childNodes[0].innerHTML.slice(1));
                    dataRow[cols[col]] = value;
                    dataRow['order_link'] = data[col].childNodes[0].href;
                    break;                
                case 'status':
                    dataRow[cols[col]] = data[col].childNodes[0].innerHTML;
                    break;
                default:
                    dataRow[cols[col]] = data[col].innerHTML;
                    break;
            }
        }
        dataTable.push(dataRow);
    })
    
    /*for (let i=1; i < rows.length; i++){
        var row_data = {};
        for (let col in cols) {
            let data = rows[i].cells;
            if (cols[col] === 'order'){
                let value = parseInt(data[col].childNodes[0].innerHTML.slice(1));
                row_data[cols[col]] = value;
                row_data['order_link'] = data[col].childNodes[0].href;
            } else if (cols[col] === 'total'){
                let value = parseFloat(data[col].innerHTML.slice(1));
                row_data[cols[col]] = value;
            } else if (cols[col] === 'status'){
                row_data[cols[col]] = data[col].childNodes[0].innerHTML;
            }
            else {
                row_data[cols[col]] = data[col].innerHTML;
            }
            
        }
        data.push(row_data);
    }*/
    return dataTable;
}

//Order data array by field. Return data ordered
function orderDataBy(data, by='date', asc=false){
    let order = (asc)?1:-1;
    let status = getData('status_options');
    const newData = [...data];

    newData.sort(function (a,b){
        
        if (by === 'status'){
            if (status.indexOf(a[by]) > status.indexOf(b[by])) return order;
            if (status.indexOf(a[by]) < status.indexOf(b[by])) return -order;
        } else {
            if (a[by] > b[by]) return order;
            if (a[by] < b[by]) return -order;
        }
        
        return 0;
    });
    return newData;
}

//Get data from table, ordering and show
function orderTableBy(table, field='date', asc=false){
    let data = getDataFromTable(table);

    data = orderDataBy(data, field, asc);
    deleteTableContent(table);
    createTable(data);
}

//Show a hidden row
function showRow(row){
    if (row.classList.contains('inactive')){
        row.classList.remove('inactive');
    }
}

//Hide a row
function hideRow(row){
    if (!row.classList.contains('inactive')){
        row.classList.add('inactive');
    }
}

//Hide all rows in table
function hideTable(table){
    let rows = Array.from(table.rows).slice(1);
    rows.map(hideRow);
}

//Display maxrows of the table and the page
function showTable(table, page=1){
    //Calculate the page number
    const rows = Array.from(table.rows).slice(1);
    const maxrows = document.getElementById('maxrows').value;
    let maxpage = Math.ceil(rows.length/maxrows);
    //page could not be grater than maxpage
    page = (page <= maxpage)?page:maxpage;
    //page could not be less than 1
    page = (page < 1)?1:page;
    
    //Calculate the init index and final index
    let init_idx = (page-1) * maxrows;
    let final_idx = (rows.length >= page*maxrows)?(page*maxrows):rows.length;
    let show_rows = rows.slice(init_idx, final_idx);
    
    //Hide the table
    hideTable(table);
    //Show the rows
    show_rows.map(showRow);
    //Update the pagination
    selectPagePagination(page);
}

//Create the pagination of table
function createPagination(numrows, rowsPerPage=20){
    const pagination = document.getElementById('pagination');
    const htmlContent = document.createDocumentFragment();
    
    //Create the prev and next page buttom
    const prev = document.createElement('span');
    const next = document.createElement('span');

    prev.classList.add('pagination-element', 'pagination-prev');
    prev.innerHTML = '<i class="fas fa-caret-left"></i>'
    next.classList.add('pagination-element', 'pagination-next');
    next.innerHTML = '<i class="fas fa-caret-right"></i>'

    //Add the prev button to fragment
    htmlContent.appendChild(prev);

    // Calculate the pages
    let pages = Math.ceil(numrows/rowsPerPage);

    for (let i=0; i < pages; i++){
        //Create the span element
        let page = document.createElement('span');
        page.classList.add('pagination-element', 'pagination-page');
        if (i === 0) {
            page.classList.add('pagination-selected');
        }
        page.innerHTML = i + 1;

        //Add to fragment
        htmlContent.appendChild(page);
    }
    //Add the next button fragment
    htmlContent.appendChild(next);

    /*Create the select maxrows to show*/
    //Create the label
    const labelSelect = document.createElement('label');
    labelSelect.setAttribute('for', 'maxrows')
    labelSelect.classList.add('pagination-selector');
    labelSelect.textContent = 'max rows'

    const maxrows = document.createElement('select');
    maxrows.setAttribute('id', 'maxrows');
    maxrows.setAttribute('name', 'maxrows');
    maxrows.classList.add('pagination-selector');

    let maxOptions = [2, 5, 10, 20, 50];
    
    maxOptions.forEach(opt => {
        let option = document.createElement('option');
        option.setAttribute('value', opt);
        if (opt === rowsPerPage) option.setAttribute('selected', true);
        option.innerHTML = opt;
        maxrows.append(option);
    });

    //Add the selector maxrows to fragment
    htmlContent.appendChild(labelSelect);
    htmlContent.appendChild(maxrows);

    //Erase the div pagination and
    //Add the fragment to div pagination
    pagination.innerHTML = "";
    pagination.append(htmlContent);
}

//Select the page of pagination. Return the current page selected.
function selectPagePagination(numPage) {
    let page = numPage;
    const pages = document.querySelectorAll('.pagination-page');
    let maxpages = pages.length;
    
    //Set the limit of page
    if (page < 1) page=1;
    if (page > maxpages) page = maxpages;

    //Put the class 'pagination-selected' in the page selected
    pages.forEach(p => {
        (p.textContent == page)?p.classList.add('pagination-selected'): p.classList.remove('pagination-selected');
    })

    return page;
}

function loadTableEvents(){
    const table = document.getElementById('orders-table');

    document.addEventListener('click', function(e){
        // Update Table Button
        if (e.target.id === 'update-table'){
            console.log('Update the table');
            requestData();
        }

        // Order Table by Field
        if (e.target.nodeName == 'TH') {
            //Get the field and the ascendence order
            let field = e.target.dataset.field;
            let asc = JSON.parse(e.target.dataset.asc);
            //Set the ascendence order as opposite
            e.target.dataset.asc = `${!asc}`;

            //Ordering the table
            console.log(`Ordering the Table by ${field}`);
            orderTableBy(table, field, asc);
        }

        //Change Status Order
        if (e.target.classList.contains('status-order')) {
            //Get the row parent
            let row = findParentElementByTagName(e.target, 'tr');
            let order = row.cells[0].childNodes[0].innerHTML;
            let change = (e.target.textContent == 'READY')?false: confirm(`Do you want to change the status of ${order}?`);
            
            if (change) {
                changeOrderStatusRequest(order.slice(1), e.target);
            }
        }

        //Pagination prev page
        if (e.target.classList.contains('pagination-prev') || e.target.classList.contains('fa-caret-left')) {
            let page = document.querySelector('.pagination-selected');
            page = parseInt(page.innerHTML) - 1;
            page = selectPagePagination(page);
            showTable(table, page);
        }

        //Pagination next page
        if (e.target.classList.contains('pagination-next') || e.target.classList.contains('fa-caret-right')) {
            let page = document.querySelector('.pagination-selected');
            page = parseInt(page.innerHTML) + 1;
            page = selectPagePagination(page);
            showTable(table, page);
        }

        //Pagination select a page
        if (e.target.classList.contains('pagination-page')) {
            let page = parseInt(e.target.innerHTML);
            page = selectPagePagination(page);
            showTable(table, page);
        }

    }, false);

    document.addEventListener('change', (e) => {
        if (e.target.id === 'maxrows'){
            let rowsPerPage = parseInt(e.target.value);
            createPagination(table.rows.length - 1, rowsPerPage);
            showTable(table, 1);
        }
    }, false);
}

function loadSearchEvents(){
    const table = document.getElementById('orders-table');
    
    document.addEventListener('click', function(e){
        // Create a new filter field
        if (e.target.id === 'add-filter') {
            // Limit the filters to three
            let filters = document.getElementsByClassName('filter-search');
            if (filters.length < 3){
                let new_filter = filters[0].cloneNode(true);
                let btn_close = document.createElement('button');
                btn_close.innerHTML = '<i class="fa fa-close"></i>';
                btn_close.classList.add('close-btn', 'btn', 'btn-warning');

                new_filter.appendChild(btn_close);
                filters[filters.length-1].parentNode.insertBefore(new_filter, filters[filters.length-1].nextSibling);
            }
        }
        
        //Delete a filter field
        if (e.target.classList.contains('close-btn') || findParentElementByClass(e.target, 'close-btn')) {
            let filter = findParentElementByClass(e.target, 'filter-search');
            filter.parentNode.removeChild(filter);
            console.log('Removing filter.');
        }

        //Collect the fields and fields-values to filter the table
        if (e.target.id === 'search-btn') {
            //Get Input Data
            let fields = document.getElementsByName('field');
            let values = document.getElementsByName('field-value');
            let search = {};
            //Extrac the values to an Array
            fields = Array.prototype.map.call(fields, field => field.value);
            values = Array.prototype.map.call(values, entry => entry.value);
            
            if (values.filter(entry => entry).length > 0) {
                search = fields.reduce((acc, cur, idx)=>({...acc, [cur]:values[idx]}), {});   
            }
            //Request the data filtered and create the table
            requestData(search);
        }
    }, false);

    document.addEventListener('input', function(e) {
        
        if(e.target.name === 'field-value') {
            let value = e.target.value.toLowerCase();
            //Remove initials withspaces
            const regExp = /^\s+|\s+$/g;
            e.target.value = value.replace(regExp, '');
        }
    }, false);
}

//Load the events after the DOM was loaded.
document.addEventListener('DOMContentLoaded', () => {
    
    // Load the events
    loadTableEvents();  //Function in this file
    loadSearchEvents(); //Function in this file

    //Load the data and create the table
    requestData(); //Function in this file
});
