from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse

import json

from .models import *
from shoppingcart.models import ShoppingCart, Order, OrderItem

# Create your views here.

def index(request):
    '''
    Render the Index Page.
    '''
    context = {
        'menu': {'platters': MenuItem.objects.select_related(),
                'products': Product.objects.select_related(),
                'prices': PriceList.objects.select_related(),
                'toppings': Topping.objects.select_related(),
                },
    }
    
    if not request.user.is_authenticated:
        return render(request, "orders/index.html", context)

    return HttpResponseRedirect(reverse("orders:profile"))

def profile(request):
    '''
    Render the Profile Page if user is login, otherwise redirect to Index Page.
    '''
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("orders:index"))
    
    context = {
        'menu': {'platters': MenuItem.objects.select_related(),
                'products': Product.objects.select_related(),
                'prices': PriceList.objects.select_related(),
        },
    }
    
    #Add User information
    context['user'] = request.user
    shop_cart = ShoppingCart.from_cookie(request)
    context['shopping_cart'] = shop_cart

    if not shop_cart:
        shop_cart = ShoppingCart(user=request.user)
        context['shopping_cart'] = shop_cart

        response = render(request, "orders/profile.html", context)
        response = shop_cart.to_cookie(request, response)

        return response

    return render(request, "orders/profile.html", context)

def owner_login(request):
    '''
    If user has Staff Permission redirect to Orders Manage Page, otherwise 
    redirect to Login Page.
    '''
    #Check user is staff and is login
    if request.user.is_authenticated and request.user.is_staff:
        return HttpResponseRedirect(reverse('orders:owner_orders'))

    return HttpResponseRedirect(reverse("registration:owner_login"))

def owner_orders(request):
    '''
    If user has Staff Permission render Orders Manage Page, otherwise 
    redirect to Index Page.
    '''
    #Check user is staff and is login
    if request.user.is_authenticated and request.user.is_staff:
        context = {
            'orders': Order.objects.select_related()
        }

        return render(request, 'orders/orders_manage.html', context)
    return HttpResponseRedirect(reverse('orders:index'))

def owner_items(request, order):
    '''
    If user has Staff Permissions render Order Items Manage, otherwise
    redirect to Index Page.
    '''

    if not (request.user.is_authenticated and request.user.is_staff):
        return HttpResponseRedirect(reverse('orders:index'))
    
    context = {
        'order': Order.objects.select_related().get(order_number=order),
        'items': OrderItem.objects.select_related().filter(order=order)
    }

    return render(request, 'orders/order_items_manage.html', context)

def api_products_data(request):
    '''
    Return a JsonResponse with Products Data if request is POST,
    otherwise return and JsonResponse with an error message.
    '''

    if request.method == 'POST':
        res = {}
        for product in Product.objects.select_related():
            res[product.id] = product.get_data()
        
        return JsonResponse({'success': True, 'products': res})
    return JsonResponse({'success': False, 'error': 'The request method must be POST.'})  

