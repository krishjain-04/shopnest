from django.contrib import admin

from .models import (
    Category,
    SubCategory,
    ThirdCategory,
    Brand,
    Product,
    ProductImage,
    Review,
    Wishlist,  # NEW
)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'created_at')
    search_fields = ('name',)
    list_filter = ('category',)
    prepopulated_fields = {'slug': ('name',)}


class ThirdCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'subcategory', 'created_at')
    search_fields = ('name',)
    list_filter = ('subcategory',)
    prepopulated_fields = {'slug': ('name',)}


class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'brand',
        'price',
        'stock',
        'is_featured',
        'is_available'
    )

    search_fields = (
        'name',
        'brand__name'
    )

    list_filter = (
        'brand',
        'is_featured',
        'is_available'
    )

    prepopulated_fields = {
        'slug': ('name',)
    }


class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product',)


# NEW: Wishlist Admin
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    search_fields = ('user__username', 'user__email', 'product__name')
    list_filter = ('created_at',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(ThirdCategory, ThirdCategoryAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
admin.site.register(Review)
admin.site.register(Wishlist, WishlistAdmin)  # NEW