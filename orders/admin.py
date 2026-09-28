from django.contrib import admin
from .models import Address, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'price', 'quantity', 'subtotal')
    can_delete = False


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone', 'city', 'state', 'pincode', 'is_default', 'created_at')
    list_filter = ('is_default', 'state', 'created_at')
    search_fields = ('user__username', 'user__email', 'full_name', 'phone', 'pincode', 'city')
    list_editable = ('is_default',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'total_amount', 'status', 'payment_method', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_method', 'payment_status', 'created_at')
    search_fields = ('order_id', 'user__username', 'user__email', 'address__full_name', 'address__phone')
    list_editable = ('status', 'payment_status')
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'price', 'quantity', 'subtotal')
    search_fields = ('order__order_id', 'product__name')