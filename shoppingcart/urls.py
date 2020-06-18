from django.urls import path

from . import views

app_name = 'shoppingcart'
urlpatterns = [
    path("add", views.add_item, name="add_item"),
    path("remove/<uuid:item>", views.remove_item, name="remove_item"),
    path("checkout", views.checkout_payment, name="checkout"),
    path("pay/success", views.checkout_success, name="success_pay"),
    path("pay/cancel", views.checkout_cancel, name="cancel_pay"),
    path("update_quantity/<uuid:item>", views.update_item_quantity),
    path("data_item/<uuid:item>", views.data_item),
    path("edit_item/<uuid:item>", views.edit_item_in_cart, name="edit_item"),
    path("api/orders", views.api_orders_data),
    path("api/chage-status", views.api_change_order_status),
    path("api/get-order-status", views.api_get_order_status),
    path("<str:username>/orders", views.show_orders, name="orders_user"),
    path("<str:username>/cart", views.show_cart, name="user_cart"),
]
