from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('search/', views.search_products, name='search_products'),
    path('categories/', views.all_categories, name='all_categories'),
    path('categories/<slug:category_slug>/', views.category_detail, name='category_detail'),
    path('categories/<slug:category_slug>/<slug:subcategory_slug>/', views.subcategory_detail, name='subcategory_detail'),
    path('categories/<slug:category_slug>/<slug:subcategory_slug>/<slug:third_slug>/', views.thirdcategory_detail, name='thirdcategory_detail'),
    
    # NEW: Wishlist URLs
    path('wishlist/', views.wishlist_view, name='wishlist_detail'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
]