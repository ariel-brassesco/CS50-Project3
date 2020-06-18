from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.html import strip_tags

import json

from .models import ShoppingCart, Order

import stripe
from pizza.settings import STRIPE_SECRET_API_KEY, EMAIL_SENDER
# Create your views here.

def add_item(request):
    
    if request.method == 'POST':
        # Load the shopping cart from cookies
        shop_cart = ShoppingCart.from_cookie(request)

        if not shop_cart:
            return HttpResponseRedirect(reverse("orders:profile"))

        # Create and add the item
        res = {}
        res['success'] = shop_cart.create_and_add_item(request=request)

        if not res['success']:
            res['error'] = 'An error was ocurred. Try again please.'
        # Save the shopping cart in cookies
        response = JsonResponse(res)
        response = shop_cart.to_cookie(request, response)
        return response
    return JsonResponse({'success': False, 'error': "Method must be GET."})

def remove_item(request, item=None):
    
    if item:
        # Load the shopping cart from cookies
        shop_cart = ShoppingCart.from_cookie(request)

        if not shop_cart:
            return HttpResponseRedirect(reverse("orders:profile"))

        # Create and add the item
        shop_cart.remove_item(id_item=item)
        print(request.META['HTTP_REFERER'])
        # Save the shopping cart in cookies
        response = HttpResponseRedirect(request.META['HTTP_REFERER'])
        response = shop_cart.to_cookie(request, response)

        return response
    
    return HttpResponseRedirect(reverse("orders:profile"))
    
def show_orders(request, username):

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("orders:index"))

    context = {
        'user': request.user,
        'orders': Order.objects.select_related().filter(user=request.user)
        }

    return render(request, "shoppingcart/orders_user.html", context)

def show_cart(request, username):

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("orders:index"))
    
    shop_cart = ShoppingCart.from_cookie(request)
    context = {
        'user': request.user,
        'shopping_cart': shop_cart
        }

    return render(request, "shoppingcart/user_cart.html", context)

def checkout_payment(request):
    if request.method == 'POST':
        # Set your secret key. Remember to switch to your live secret key in production!
        # See your keys here: https://dashboard.stripe.com/account/apikeys
        stripe.api_key = STRIPE_SECRET_API_KEY

        # Load the shopping cart from cookies
        shop_cart = ShoppingCart.from_cookie(request)

        # Checkout cart if it's not empty 
        if shop_cart.is_empty:
            return JsonResponse({'success': False, 'error': 'The cart is empty'})

        # Delivery info
        shop_cart.set_delivery_data(request.POST['deli-mode'],
                                    request.POST['delivery-address'],
                                    request.POST['delivery-appartment'],
                                    request.POST['delivery-information'])
        # Product data
        name = shop_cart.user.username
        description = '\n'.join(map(str, shop_cart.items))
        price = int(shop_cart.total * 100)
        # Session urls response
        success_url = f"{request.scheme}://{request.get_host()}{reverse('shoppingcart:success_pay')}?session_id="+"{CHECKOUT_SESSION_ID}"
        cancel_url = f"{request.scheme}://{request.get_host()}{reverse('shoppingcart:cancel_pay')}"
        
        try:
            product = stripe.Product.create(name=name, description=description)
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                    'unit_amount': price,
                    'currency': 'usd',
                    'product': product.id,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
            )
            # Save the session id in shopping cart
            shop_cart.set_session(session.id)

            response = JsonResponse({'success': True, 'session': session.id})
            response = shop_cart.to_cookie(request, response)
        except Exception as e:
            print(e)
            return JsonResponse({'success': False, 'error': e})
        return response
    return JsonResponse({'success': False, 'request-error': 'The request method must be POST.'})

def checkout_success(request):
    # Load the shopping cart from cookies
    shop_cart = ShoppingCart.from_cookie(request)

    # Checkout cart if it's not empty 
    if shop_cart.is_empty:
        return HttpResponseRedirect(reverse("orders:profile"))
    
    session_id = request.GET['session_id']
    if not shop_cart.checkout(session=session_id):
        return HttpResponseRedirect(reverse("shoppingcart:cancel_pay"))

    # Save the shopping cart in cookies
    response = HttpResponseRedirect(reverse("shoppingcart:orders_user", kwargs={'username': shop_cart.user.username}))
    response = shop_cart.to_cookie(request, response)
    
    return response

def checkout_cancel(request):
    print('Cancel Payment')
    return HttpResponseRedirect(reverse("orders:profile"))

@csrf_exempt
def update_item_quantity(request, item):
    
    if request.method == 'POST':
        # Load the shopping cart from cookies
        shop_cart = ShoppingCart.from_cookie(request)

        # Check if item exist
        if not shop_cart.has_item(item):
            return JsonResponse({'success':False, 'error': 'The item does not exist.'})

        # Update Item quantity
        quantity = int(request.POST['quantity'])
        new_price_item, new_total_cart = shop_cart.update_item_quantity(item, quantity)
        
        res = {
            'success': True,
            'price_item': new_price_item,
            'new_total': new_total_cart
        }
        response = JsonResponse(res)
        response = shop_cart.to_cookie(request, response)
    else: 
        res = {
            'success': False,
            'error': 'Not allow GET request'
        }
        response = JsonResponse(res)
    
    return response

def data_item(request, item):
    if request.method == 'POST':
        # Load the shopping cart from cookies
        shop_cart = ShoppingCart.from_cookie(request)

        # Check if item exist
        if not shop_cart.has_item(item):
            return JsonResponse({'success':False, 'error': 'The item does not exist.'})
        
        cart_item = shop_cart.get_item(item)
        
        context = {
            'cart_item': cart_item,
            'product': cart_item.product,
            'presentations': cart_item.product.get_presentations(),
            'sizes': cart_item.product.get_sizes(),
            'additionals': cart_item.product.additional.select_related(),
        }

        page = render_to_string('shoppingcart/form_edit_item.html', context=context)

        res = {
            'success': True,
            'page': page
        }
        response = JsonResponse(res)
    else: 
        res = {
            'success': False,
            'error': 'Not allow GET request'
        }
        response = JsonResponse(res)
    return response

def edit_item_in_cart(request, item):
    if request.method == 'POST':
        # Load the shopping cart from cookies
        shop_cart = ShoppingCart.from_cookie(request)
        # Check if item exist
        if not shop_cart.has_item(item):
            return JsonResponse({'success':False, 'error': 'The item does not exist.'})
        
        # Update Item Data
        product = int(request.POST['product'])
        size = None if 'size' not in request.POST else int(request.POST['size'])
        presentation = None if 'presentation' not in request.POST else int(request.POST['presentation'])
        quantity = int(request.POST['item-quantity'])
        additionals = [] if 'additionals' not in request.POST else request.POST.getlist('additionals')
        
        cart_item = shop_cart.get_item(item)
        update = cart_item.update(product, size, presentation, additionals, quantity)
        
        # Check Update status
        if update:
            res = {
                'success': True,
            }
        else: 
            res = {
                'success': False,
                'error': 'Data Error. Try Again please.'
            } 
        response = JsonResponse(res)
    else: 
        res = {
            'success': False,
            'error': 'Not allow GET request'
        }
        response = JsonResponse(res)
    # Save the cart changes
    response = shop_cart.to_cookie(request, response)
    return response

def api_orders_data(request):

    if (request.method == 'POST') and request.user.is_staff:
        filters = request.POST['filters']
        filters = json.loads(filters)

        data = []
        orders = filter_orders(filters)
        for order in orders:
            data.append({'order': order.order_number,
                        'order_link': reverse('orders:owner_order_items', args= (order.order_number,)),
                        'date': order.date_order,
                        'username': order.user.username,
                        'delivery': order.get_deli_mode_display(),
                        'address': order.address,
                        'total': order.total,
                        'status':order.get_status_display(),
                        })
        
        res = {
            'success': True,
            'orders': data,
            'status_options': list(map(lambda state: state[1].upper(), Order.STATUS_CHOICES)),
            'columns': ['order', 'date', 'username', 'delivery', 'address', 'total', 'status'],
        }
        return JsonResponse(res)
    return JsonResponse({'success': False, 'error': 'The request method must be POST.'})

def filter_orders(filters):
    #Get all the orders
    orders = Order.objects.select_related()
    #Apply filters
    for k, v in filters.items():
        if (k == 'order'):
            #v[1:] to eliminate '#'
            orders = orders.filter(order_number__icontains=v)
        if (k == 'username'):
            orders = orders.filter(user__username__icontains=v)
        if (k == 'delivery'):
            # v[0] only take 'T' or 'D'
            orders = orders.filter(deli_mode__icontains=v[0])
        if (k == 'address'):
            orders = orders.filter(address__icontains=v)
        if (k == 'status'):
            #Filter the STATUS_CHOICES
            sta = list(filter(lambda x: v.lower() in x[1].lower(), Order.STATUS_CHOICES))
            #Select the orders which status is less or equal to the greater sta value
            orders = orders.filter(status__lte=sta[-1][0])
    #Return the orders filtered list
    return orders

def api_get_order_status(request):
    
    if request.user.is_authenticated:
        return JsonResponse({'success': True, 'status': Order.STATUS_CHOICES})

    return JsonResponse({'success': False, 'error': 'Only login users.'})

def api_change_order_status(request):
    
    if (request.method == 'POST') and request.user.is_staff:
        order_number = request.POST['order']

        try:
            order = Order.objects.get(order_number=order_number)
            new_status = int(order.status) + 1
            prev_status, new_status = order.set_status(new_status)
            email = False
            if not (new_status == prev_status):
                email = True
                #Send User email
                template_email = 'shoppingcart/change_order_status.html'
                subject = f'Order {str(order)} Information'
                from_email = EMAIL_SENDER
                context = {
                    'user': order.user,
                    'order': str(order),
                    'status': order.get_status_display(),
                }
                
                send_email_user(template_email, context, subject ,from_email, order.user)
                
            return JsonResponse({
                    'success': True,
                    'prev_status': prev_status,
                    'new_status': new_status,
                    'email': email,
                    })
        except Order.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'order',
                'message': 'The order number does not exist.'
                })
    return JsonResponse({
            'success': False,
            'error': 'request',
            'message': 'The request method must be POST.'
            })

def send_email_user(template, context, subject, from_email, user):
    # Set email data
    html_message = render_to_string(template, context=context)
    message = strip_tags(html_message)
    # Send email
    user.email_user(subject, message, from_email, html_message=html_message)
