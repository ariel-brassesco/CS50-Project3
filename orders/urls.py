from django.urls import path

from . import views

app_name = 'orders'
urlpatterns = [
    path("", views.index, name="index"),
    path("profile", views.profile, name="profile"),
    path("owner", views.owner_login, name="owner_login"),
    path("owner/orders", views.owner_orders, name="owner_orders"),
    path("owner/orders/<int:order>", views.owner_items, name="owner_order_items"),
    path('api/products', views.api_products_data),
]
