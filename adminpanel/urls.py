from django.urls import path
from .views import *


urlpatterns=[


   path("login/",admin_login,name="admin_login"),
   path("logout/",admin_logout,name="admin_logout"),
   path("dashboard/",admin_dashboard,name="admin_dashboard"),

   path("categories/",category_list,name="admin_categories"),
   path('categories/add/',add_category, name='add_category'),
   path('categories/delete/<int:id>/',delete_category, name='delete_category'),

   path("subcategories/",subcategory_list,name='admin_subcategories'),
   path("subcategories/add/",add_subcategory,name='add_subcategory'),
   path("subcategories/delete/<int:id>",delete_subcategory,name="delete_subcategory"),

   path('thirdcategories/',thirdcategory_list, name='admin_thirdcategories'),
   path('thirdcategories/add/',add_thirdcategory, name='add_thirdcategory'),
   path('thirdcategories/delete/<int:id>/',delete_thirdcategory, name='delete_thirdcategory'),

   path('brands/',brand_list, name='admin_brands'),
   path('brands/add/',add_brand, name='add_brand'),
   path('brands/delete/<int:id>/',delete_brand, name='delete_brand'),


   path('products/',product_list, name='admin_products'),
   path('products/add/',add_product, name='add_product'),
   path('products/edit/<int:id>/',edit_product, name='edit_product'),
   path('products/delete/<int:id>/',delete_product, name='delete_product'),
   path('products/delete-image/<int:id>/',delete_product_image, name='delete_product_image'),

   path('orders/', order_list, name='admin_orders'),
   path('orders/detail/<int:id>/',order_detail, name='admin_order_detail'),
   path('orders/invoice/<int:id>/',admin_download_invoice, name='admin_download_invoice'),
   path('orders/update-status/<int:id>/',update_order_status, name='update_order_status'),

   path('users/',user_list, name='admin_users'),
   path('users/detail/<int:id>/',user_detail, name='admin_user_detail'),
   path('users/toggle-status/<int:id>/',toggle_user_status, name='toggle_user_status'),



   path(
    'get-subcategories/',get_subcategories,
    name='get_subcategories'
   ),

   path(
    'get-thirdcategories/',get_thirdcategories,
    name='get_thirdcategories'
   ), 

   path(
    'get-brands/',get_brands,
    name='get_brands'
   ),
   path('brands/edit/<int:id>/', edit_brand, name='edit_brand'),









path('sliders/', slider_list, name='admin_sliders'),
path('sliders/add/', add_slider, name='add_slider'),
path('sliders/edit/<int:id>/', edit_slider, name='edit_slider'),
path('sliders/delete/<int:id>/', delete_slider, name='delete_slider'),
path('sliders/toggle/<int:id>/', toggle_slider, name='toggle_slider'),


   
   ]
