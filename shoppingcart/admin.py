from django.contrib import admin

# Register your models here.
from .models import OrderItem, Order

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order', 'username', 'total', 'date_order', 'status')

    ordering = ('-status', 'date_order')

    def username(self, obj):
        return obj.user.username
    
    def order(self, obj):
        return str(obj)

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'presentation',
        'size', 'additional', 'quantity',
        'price_unitary', 'total')
    
    ordering = ('id',)


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
