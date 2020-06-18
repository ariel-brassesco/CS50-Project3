from django import template
from ..models import PriceList

register = template.Library()

@register.filter(name='get')
def get_item(var, key):
    return var.get(key)

@register.filter(name='price')
def get_price(var, size=None):
    try:
        res = var.get(size=size).price
    except PriceList.DoesNotExist:
        return ''
    return res

@register.filter(name='get_variation')
def get_variation(var, presentation):
    return var.pricelist_set.filter(presentation=presentation)

@register.filter(name='food_name')
def food_name(var, food):
    if var.variation == 'Normal':
        return food.name
    return var.variation

@register.filter(name='dolar_sign')
def dolar_sign(var):
    if var:
        return f"$ {var}"
    return var

# Return a range of number
# Counter says if star form '0' or '1'
@register.filter(name='times') 
def times(number, counter):
    if counter:
        return range(1,number+1)
    return range(number)

@register.filter(name='mult') 
def mult(n1, n2):
    return n1*n2

@register.filter(name='sum') 
def sum(n1, n2):
    return n1+n2