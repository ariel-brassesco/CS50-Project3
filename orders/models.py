from django.db import models
from django.db.models import Min

# Models for products.

class MenuItem(models.Model):
    item_type = models.CharField('Menu Item', max_length=30, unique=True)

    def __str__(self):
        return self.item_type
    
    def get_sizes(self):
        sizes = self.sizes.select_related().order_by('id')
        return sizes

class ProductSize(models.Model):
    item_size = models.CharField('Size', max_length=20, unique=True)
    item_type = models.ManyToManyField(MenuItem, related_name='sizes')

    def __str__(self):
        return self.item_size

class ProductVariation(models.Model):
    
    variation = models.CharField('Variation', max_length=20, unique=True)
    type_variation = models.CharField(max_length=20, default='base')

    def __str__(self):
        return self.variation
    
    def is_base(self):
        return self.type_variation == 'base'

class Topping(models.Model):
    topping_type = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    topping = models.CharField('Topping', max_length=30)
    price = models.FloatField('Price', default=0.0)

    def __str__(self):
        return f"{self.topping} ({self.topping_type})"
    
    def is_for_all(self):
        menu_products = self.topping_type.product_set.select_related()
        topping_products = self.additional.select_related()

        if len(menu_products) == len(topping_products):
            return True
        return False

class Product(models.Model):
    menu_type = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    name = models.CharField('Product', max_length=100)
    description = models.TextField('Description', max_length=400, blank=True)
    additional = models.ManyToManyField(Topping, blank=True, related_name='additional')
    image = models.ImageField(upload_to='products/%Y/%m/%d')
    max_add = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.menu_type}: {self.name}"

    def get_sizes(self):
        sizes = self.menu_type.get_sizes()
        return sizes
    
    def get_presentations(self):
        presentations = self.pricelist_set.values('presentation').distinct()
        variations = []
        for p in presentations:
            variation = ProductVariation.objects.get(pk=p['presentation'])
            variations.append(variation)
        return variations
    
    def get_price_min(self):
        return self.pricelist_set.aggregate(Min('price'))
    
    def get_data(self):
        data = {}
        # Get the prices for each variation and size
        for variation in self.get_presentations():
            
            data[variation.id] = {}
            data[variation.variation] = {}
            for size in self.get_sizes():
                try:
                    data[variation.id][size.id] = self.pricelist_set.get(presentation=variation, size=size).price
                    data[variation.variation][size.item_size] = self.pricelist_set.get(presentation=variation, size=size).price
                except PriceList.DoesNotExist:
                    pass
            
            if not self.get_sizes():
                try:
                    data[variation.id] = self.pricelist_set.get(presentation=variation).price
                    data[variation.variation] = self.pricelist_set.get(presentation=variation).price
                except PriceList.DoesNotExist:
                    pass

        #Get the prices for each topping
        data['additionals'] = {}
        data['additionals']['max'] = self.max_add
        for additional in self.additional.select_related():
            data['additionals'][additional.id] = additional.price

        return data

# Models for Prices
class PriceList(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    presentation = models.ForeignKey(ProductVariation, null=True, on_delete=models.SET_NULL)
    size = models.ForeignKey(ProductSize, blank=True,null=True, on_delete=models.SET_NULL)
    price = models.FloatField('Price', default=0.0)

    def __str__(self):
        if self.presentation.variation == 'base':
            return f'{self.product} ({self.size}): $ {self.price}'
        return f'{self.product} + {self.presentation} ({self.size}): $ {self.price}'

# Model for Restaurant information
class OpenHours(models.Model):
    time = models.TimeField()
    def __str__(self):
        return self.get_AMPM_time()
    
    def get_AMPM_time(self):
        if (self.time.hour <= 12):
            return f"{self.time.hour:02}:{self.time.minute:02} AM"
        return f"{self.time.hour-12:02}:{self.time.minute:02} PM"

class Schedule(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Sunday'),
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday')
    ]

    day = models.IntegerField(choices=DAYS_OF_WEEK, default=1)
    hour_from = models.ForeignKey(OpenHours, on_delete=models.CASCADE, related_name="hourfrom")
    hour_to = models.ForeignKey(OpenHours, on_delete=models.CASCADE, related_name="hourto")

    def __str__(self):
        return f"{self.get_day_display()}: {self.hour_from}-{self.hour_to}"

class Place(models.Model):
    name = models.CharField('Restaurant', max_length=100)
    address = models.CharField('Address', max_length=150)
    phone_number = models.CharField('Phone Number', max_length=17)
    image = models.ImageField(upload_to='owner/%Y/%m/%d')
    schedule = models.ManyToManyField(Schedule, related_name="opening")

    def __str__(self):
        return self.name

    def get_phone(self):
        phone = self.phone_number
        return '-'.join([phone[:3], phone[3:6],phone[6:]])
    
    def get_schedule(self):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Fridat', 'Saturday', 'Sunday']
        lst = [[] for _ in range(7)]

        for schedule in self.schedule.order_by('day'):
            lst[schedule.day].append([schedule.hour_from, schedule.hour_to])
        # Move Sunday to the last position
        last = lst[0]
        del lst[0]
        lst.append(last)

        return tuple(zip(days, lst))

