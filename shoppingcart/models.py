from django.db import models
from django.contrib.auth.models import User
import json
import uuid

from orders.models import Product, ProductSize, ProductVariation, Topping, PriceList

# Create your models here.
class ItemCart():

    def __init__(self, product=None, size=None, presentation=None,
                additional=[], quantity=1):
        
        self.id = uuid.uuid4()
        self.product = product
        self.presentation = presentation
        self.size = size
        self.additional = additional
        self.unitary_price = self.get_unitary_price()
        self.quantity = quantity
        self.total_price = self.set_total_price()

    def get_unitary_price(self):
        additional_cost =  0.0

        for additional in self.additional:
            additional_cost += additional.price
        try:
            p = PriceList.objects.get(product=self.product,
                                presentation=self.presentation,
                                size=self.size)
        except:
            return 0.0
        return p.price + additional_cost

    def set_total_price(self):
        return self.quantity * self.unitary_price

    def set_quantity(self, quantity):
        self.quantity = quantity
        self.total_price = self.set_total_price()

    def create_orderitem(self, order):

        try:
            OrderItem.objects.get(item_id=self.id)
            return False

        except OrderItem.DoesNotExist:
            
            additional = ''
            if self.additional:
                additional = ', '.join(map(lambda x: x.topping, self.additional))

            new_item =OrderItem(order=order,
                        item_id=self.id,
                        quantity=self.quantity,
                        product = self.product.name,
                        presentation = self.presentation.variation,
                        size = '' if not self.size else self.size.item_size,
                        additional = additional,
                        price_unitary = self.unitary_price,
                        total = self.total_price)
            
            new_item.save()
            
            return True

    def update(self, product, size, presentation, additionals, quantity):
        # Check the product is the same
        if self.product.id != product: return False
        sizes = self.product.get_sizes()
        presentations = self.product.get_presentations()
        
        try:
            toppings = [self.product.additional.get(id=top) for top in additionals]
        except Topping.DoesNotExist:
            print('A Topping in additionals list is not valid.')
            return False

        # Check the data is correct
        if size and (size not in map(lambda s: s.id, sizes)): return False
        if presentation and (presentation not in map(lambda p: p.id, presentations)): return False
        if not (1 <= quantity <= 10): return False
        
        # Set the attributes to the new values
        if size: self.size = sizes.get(id=size)
        if presentation: self.presentation = list(filter(lambda p: p.id == presentation, presentations))[0]
        self.additional = toppings
        self.set_quantity(quantity)
        # Set the new prices values
        self.unitary_price = self.get_unitary_price()
        self.total_price = self.set_total_price()

        return True

    def __str__(self):
        return str(self.product)

class ShoppingCart():
    
    def __init__(self, user=None, deli_mode = 'T', address=None, items=[], session=None):
        
        self.user = user
        self.items = items
        self.deli_mode = deli_mode
        self.address = address
        self.is_empty = not items
        self.total = self.total_cost(items)
        self.session = session

    def add_item(self, item):
        self.items.append(item)
        self.total += item.total_price
        # Update the is_empty state
        self.is_empty = not self.items

    def remove_item(self, id_item):
        # Remove the item from items
        for item in self.items:
            if item.id == id_item:
                self.total -= item.total_price
                self.items.remove(item)
        # Update the is_empty state
        self.is_empty = not self.items

    def create_and_add_item(self, request=None):
        if request:
            try:
                product = Product.objects.get(id=request.POST.get('product'))
                size = ProductSize.objects.filter(id=request.POST.get('size')).first()
                presentation = ProductVariation.objects.get(id=request.POST.get('presentation'))
                quantity = int(request.POST.get('item-quantity'))

                additional = []
                if request.POST.get('additionals'):
                    for ad in request.POST.getlist('additionals'):
                        topping = Topping.objects.get(id=ad)
                        additional.append(topping)
            except:
                return False

            item = ItemCart(product=product, size=size, presentation=presentation,
                            additional=additional, quantity=quantity)
        
            self.add_item(item)
            return True
        return False

    def has_item(self, id_item):
        # Search id_item in items list
        for item in self.items:
            if item.id == id_item:
                return True
        return False

    def get_item(self, id_item):
        # Search id_item in items list and return
        for item in self.items:
            if item.id == id_item:
                return item
        return False

    def total_cost(self, items):
        cost = 0
        for item in items:
            cost += item.total_price
        return cost

    def update_item_quantity(self, id_item, quantity):
        # Search id_item in items list
        # and update the quantity value
        for item in self.items:
            if item.id == id_item:
                # update item quantity
                item.set_quantity(quantity)
                break
        # Update cart total
        self.total = self.total_cost(self.items)
        return item.total_price, self.total

    def empty_cart(self):
        self.items = []
        self.deli_mode = 'T'
        self.address = None
        self.is_empty = True
        self.total = 0.0

    def set_delivery_data(self,
                    deli_mode='T',
                    address=None,
                    appartment=None,
                    more_info=None):

        self.deli_mode = deli_mode
        if deli_mode == 'D' and address:
            self.address = '\n'.join([address, appartment, more_info])
        else:
            self.address = None

    def set_session(self, session):
        self.session = session

    def checkout(self, session):
        #Check the session ID is valid
        if not (self.session == session):
            print('Incorrect Session ID')
            return False
        # Check the data is valid
        if self.deli_mode == 'D' and not self.address: return False
        new_order = Order(user=self.user, session_id=self.session, deli_mode=self.deli_mode, address=self.address, total=self.total)
        new_order.save()

        for item in self.items:
            item.create_orderitem(order=new_order)
        
        # Empty the cart
        self.empty_cart()

        return True    

    def to_JSON(self):
        return json.dumps(self, cls=ShoppingCartEncoder)
    
    def from_JSON(dct):
        return json.loads(dct, cls=ShoppingCartDecoder)
    
    def to_cookie(self, request, response):
        response.set_signed_cookie(f'cart-{request.user.id}', False)
        response.set_signed_cookie(f'cart-{request.user.id}', self.to_JSON(), max_age=31536000)
        return response

    def from_cookie(request):
        cookie_cart = request.get_signed_cookie(f'cart-{request.user.id}', False)
        if not cookie_cart:
            return False
        return json.loads(cookie_cart, cls=ShoppingCartDecoder)

class ShoppingCartEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (ItemCart, ShoppingCart)):
            res = obj.__dict__
            res['_type'] = obj.__class__.__name__
            return res
        elif isinstance(obj, (Product, ProductSize, ProductVariation, Topping, User)):
            return {'_type': obj.__class__.__name__, 'value': obj.id}
        elif isinstance(obj, uuid.UUID):
            return {'_type': 'UUID', 'value': str(obj)}
        else:
            return super().default(obj)

class ShoppingCartDecoder(json.JSONDecoder):

    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)
    
    def object_hook(self, obj):
        if '_type' not in obj:
            return obj

        if obj['_type'] == 'ShoppingCart':
            res = ShoppingCart(user=obj['user'], items=obj['items'], session=obj['session'])
            return res

        if obj['_type'] == 'ItemCart':
            res = ItemCart(product=obj['product'],
                            size=obj['size'],
                            presentation=obj['presentation'],
                            additional=obj['additional'],
                            quantity=obj['quantity'])
            res.id = obj['id']
            return res

        if obj['_type'] == 'UUID':
            return uuid.UUID(obj['value'])
        
        if obj['_type'] == 'Product':
            return Product.objects.get(id=obj['value'])

        if obj['_type'] == 'ProductSize':
            return ProductSize.objects.get(id=obj['value'])
        
        if obj['_type'] == 'ProductVariation':
            return ProductVariation.objects.get(id=obj['value'])
        
        if obj['_type'] == 'Topping':
            return Topping.objects.get(id=obj['value'])
        
        if obj['_type'] == 'User':
            return User.objects.get(id=obj['value'])

        return obj


# Models for Order Managing
class Order(models.Model):

    DELIVERY_MODES = [
        ('D','Delivery'),
        ('T','Takeaway')
    ]

    STATUS_CHOICES = [
        ('1', 'Processing'),
        ('2', 'Preparing'),
        ('3', 'Delivering'),
        ('4', 'Ready'),
    ]

    order_number = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    session_id = models.CharField(max_length=80)
    date_order = models.DateTimeField(auto_now_add=True)
    deli_mode = models.CharField(max_length=15, choices=DELIVERY_MODES, default='T')
    address = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='1')
    total = models.FloatField(default=0.0)

    def __str__(self):
        return f"#{self.order_number:05d}"
    
    def set_status(self, status):
        prev = int(self.status)
        if (prev == 4):
            return prev, prev
        if (prev == 2) and (self.deli_mode == 'T'):
            new = 4
            self.status = '4'
        else:
            new = status
            self.status = str(status)
        self.save()
        return prev, new

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    item_id = models.UUIDField()
    quantity = models.PositiveIntegerField(default=1)
    product = models.CharField(max_length=100)
    presentation = models.CharField(max_length=100)
    size = models.CharField(max_length=30, blank=True)
    additional = models.TextField(blank=True)
    price_unitary = models.FloatField(default=0.0)
    total = models.FloatField(default=0.0)

    def __str__(self):
        return f"#{self.id}"

    def save(self, *args, **kwargs):
        self.total = self.quantity*self.price_unitary
        super(OrderItem, self).save(*args, **kwargs)



