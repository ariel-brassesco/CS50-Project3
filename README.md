# Project 3

This an E-commerce Web Application for Pinocchio's Pizza & Subs for course Web Programming with Python and JavaScript. [Link to the app](https://cs50-pinocchio.herokuapp.com/)

## Description
In this web application, as an user you can singin with an username ans e-mail. When users login can add food (products) to their carts, checkout their orders, and follow the order's status.

As an owner, you can manage the orders's users, the menu and the users. I create a test 
admin user with the following credentials:
Username: admin
Password: HjoiekJi34

## Some features

### For users:
* Still login when close the browser(required).
* Your cart is saved even if you logout (required).
* Mobile Responsive Design.
* Can choose Delivery or Take Away.
* Can follow the status of your orders.
* Can pay with credit cards.

### For owner:

* Can manage the product database. Can add, delete or modify a product and will be render in the web page automatically.
* The orders's users are in a table you can filter and order by any field in ascending or descending order.
* You can manage the status of orders (Processing, Preparing, Delivery or Ready). When change the status send and e-mail to user.

## Project Structure
This web application is developed with Django. The project is called `pizza` and has three applications called `registration`, `orders` and `shoppingcart`.

The `registration` app is build with the User model of `auth` app in Django, this application manage the registration and login of users and owners.

The `shoppingcart` application manage the user's cart, the actions for add, delete or modify and item in the cart, checkout the cart and generate orders.

The `orders` application manage the menu products and the orders for owners.
