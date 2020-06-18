from django import template

register = template.Library()

@register.inclusion_tag('orders/product_tag.html')
def show_product(product, index=0):
    
    context = product.get_price_min()
    context['product'] = product
    context['index'] = index
    return context

@register.inclusion_tag('orders/form_product.html')
def form_product(product):

    return {'product': product,
            'presentations': product.get_presentations(),
            'sizes': product.get_sizes(),
            'additionals': product.additional.select_related(),
            }

@register.inclusion_tag('orders/show_place.html')
def show_place(place):

    return {'name': place.name,
            'address': place.address,
            'phone': place.get_phone(),
            'image': place.image
            }
