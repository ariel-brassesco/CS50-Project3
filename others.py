'''
from django.contrib.auth.models import User
from shoppingcart.models import ItemCart, ShoppingCart, ShoppingCartEncoder, ShoppingCartDecoder
from json import loads, dumps
import uuid
from orders.models import *

prod = Product.objects.get(id=2)
varia = ProductVariation.objects.get(variation='base')
size = ProductSize.objects.get(id=1)
toppings = list(Topping.objects.filter(topping_type=1))
user = User.objects.get(username='ariel')

item = ItemCart(product=prod, size=size, presentation=varia, additional=toppings)

shop_cart1 = ShoppingCart(user=user)
shop_cart2 = ShoppingCart(user=user, items=[item])

item_encode = dumps(item, cls=ShoppingCartEncoder)
item_decode = loads(item_encode, cls=ShoppingCartDecoder)
shop1_encode = dumps(shop_cart1, cls=ShoppingCartEncoder)
shop1_decode = loads(shop1_encode, cls=ShoppingCartDecoder)
shop2_encode = dumps(shop_cart2, cls=ShoppingCartEncoder)
shop2_decode = loads(shop2_encode, cls=ShoppingCartDecoder)

'''

import json

class Foo():

    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __eq__(self, other):
        return (self.a == other.a) and (self.b == other.b)

class Bar():

    def __init__(self, c):
        self.c = c

    def __eq__(self, other):
        return self.c == other.c


class FooEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (Foo, Bar)):
            res = obj.__dict__
            res['_type'] = obj.__class__.__name__
            return res
        
        return super().default(obj)

class FooDecoder(json.JSONDecoder):

    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)
    
    def object_hook(self, obj):
        if '_type' not in obj:
            return obj
        
        if obj['_type'] == 'Foo':
            return Foo(obj['a'], obj['b'])
        elif obj['_type'] == 'Bar':
            return Bar(obj['c'])
        
        return obj

'''
bar = Bar(5)
foo = Foo(4,bar)

bar_encode = json.dumps(bar, cls=FooEncoder)
foo_encode = json.dumps(foo, cls=FooEncoder)
bar_decode = json.loads(bar_encode, cls=FooDecoder)
foo_decode = json.loads(foo_encode, cls=FooDecoder)

print(foo)
print(bar)
print(foo_encode)
print(bar_encode)
print(bar_decode)
print(bar == bar_decode)
print(foo_decode.__dict__)
print(foo == foo_decode)
'''
foo = Foo(4, [Bar(3), Bar(4)])
foo_encode = json.dumps(foo, cls=FooEncoder)
foo_decode = json.loads(foo_encode, cls=FooDecoder)

print(foo)
print(foo_encode)
print(foo_decode.__dict__)
print(foo == foo_decode)

