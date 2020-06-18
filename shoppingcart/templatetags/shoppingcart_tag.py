from django import template
#from ..models import *

register = template.Library()


@register.inclusion_tag('shoppingcart/shopping_cart.html')
def show_cart(shopping_cart):
    return {'cart': shopping_cart}


@register.inclusion_tag('shoppingcart/cart_item.html')
def show_item(shop_item):
    res = shop_item.__dict__
    return res
