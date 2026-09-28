from django.urls import path
from . import views


urlpatterns = [

    # Checkout & Order
    path(
        'checkout/',
        views.checkout_view,
        name='checkout'
    ),

    path(
        'place-order/',
        views.place_order_view,
        name='place_order'
    ),

    path(
        'order-success/<str:order_id>/',
        views.order_success_view,
        name='order_success'
    ),

    path(
        'my-orders/',
        views.my_orders_view,
        name='my_orders'
    ),

    path(
        'order-detail/<str:order_id>/',
        views.order_detail_view,
        name='order_detail'
    ),

    path(
        'order-cancel/<str:order_id>/',
        views.cancel_order_view,
        name='cancel_order'
    ),

    path(
        'order-invoice/<str:order_id>/',
        views.download_invoice_view,
        name='download_invoice'
    ),

    # Address Management
    path(
        'addresses/',
        views.address_list_view,
        name='address_list'
    ),

    path(
        'addresses/add/',
        views.add_address_view,
        name='add_address'
    ),

    path(
        'addresses/edit/<int:pk>/',
        views.edit_address_view,
        name='edit_address'
    ),

    path(
        'addresses/delete/<int:pk>/',
        views.delete_address_view,
        name='delete_address'
    ),

    path(
        'addresses/set-default/<int:pk>/',
        views.set_default_address_view,
        name='set_default_address'
    ),
]