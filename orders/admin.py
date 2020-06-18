from django.contrib import admin

from .models import *

class ToppingInline(admin.StackedInline):
    model = Topping.additional.through
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ('menu_type',
                    'name',
                    'description')
    list_filter = ['menu_type', 'name']
    search_fields = ['name']
    ordering=['menu_type', 'name']
    filter_horizontal = ("additional",)

class ToppingAdmin(admin.ModelAdmin):
    list_display = ('topping_type', 'topping', 'price')
    ordering = ['topping']

class PriceAdmin(admin.ModelAdmin):
    list_display = ('product',
                    'presentation',
                    'size',
                    'price')

class ProductSizeAdmin(admin.ModelAdmin):
    filter_horizontal = ('item_type',)

class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('day','hour_from', 'hour_to')

class PlaceAdmin(admin.ModelAdmin):
    filter_horizontal = ('schedule',)

# Register your models here.
admin.site.register(MenuItem)
admin.site.register(ProductSize, ProductSizeAdmin)
admin.site.register(ProductVariation)
admin.site.register(Topping, ToppingAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(PriceList, PriceAdmin)
admin.site.register(OpenHours)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(Place, PlaceAdmin)