from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse

from .models import Cart, CartItem
from products.models import Product


@login_required
def cart_view(request):
    if request.method == 'GET':
        cart, _ = Cart.objects.get_or_create(user=request.user)

        cart_items = list(cart.items.select_related('product', 'product__brand').all())
        for item in cart_items:
            product = item.product
            if product.is_available and product.stock > 0 and item.quantity > product.stock:
                item.quantity = product.stock
                item.save(update_fields=['quantity'])

        cart_items = list(cart.items.select_related('product', 'product__brand').all())
        valid_items = [
            item for item in cart_items 
            if item.product.is_available and item.product.stock > 0 and item.quantity > 0
        ]

        subtotal = sum(item.total_price for item in valid_items)
        grand_total = subtotal
        total_quantity = sum(item.quantity for item in valid_items)
        product_count = len(valid_items)

        context = {
            'cart': cart,
            'cart_items': cart_items,
            'subtotal': subtotal,
            'grand_total': grand_total,
            'total_quantity': total_quantity,
            'product_count': product_count,
        }
        return render(request, 'client/cart.html', context)


@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, is_available=True)
        cart, _ = Cart.objects.get_or_create(user=request.user)

        request.session.pop('buy_now', None)
        request.session.modified = True

        try:
            qty = max(1, int(request.POST.get('quantity', 1)))
        except (TypeError, ValueError):
            qty = 1

        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if product.stock <= 0:
            msg = f"'{product.name}' is currently out of stock."
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': msg,
                    'cart_count': sum(item.quantity for item in cart.items.all()),
                    'product_id': product.id,
                    'stock': product.stock,
                }, status=400)

            messages.error(request, msg)
            return redirect('cart_view')

        cart_item = CartItem.objects.filter(cart=cart, product=product).first()

        if cart_item:
            new_quantity = cart_item.quantity + qty
            if new_quantity > product.stock:
                msg = f"Only {product.stock} unit(s) of '{product.name}' are available in stock."
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'message': msg,
                        'cart_count': sum(item.quantity for item in cart.items.all()),
                        'product_id': product.id,
                        'stock': product.stock,
                        'available_stock': max(product.stock - cart_item.quantity, 0),
                        'cart_quantity': cart_item.quantity,
                    }, status=400)

                messages.error(request, msg)
                return redirect('cart_view')

            cart_item.quantity = new_quantity
            cart_item.save(update_fields=['quantity'])
            msg = f"Updated quantity for '{product.name}'."

        else:
            if qty > product.stock:
                msg = f"Only {product.stock} unit(s) of '{product.name}' are available in stock."
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'message': msg,
                        'cart_count': sum(item.quantity for item in cart.items.all()),
                        'product_id': product.id,
                        'stock': product.stock,
                        'available_stock': product.stock,
                    }, status=400)

                messages.error(request, msg)
                return redirect('cart_view')

            cart_item = CartItem.objects.create(cart=cart, product=product, quantity=qty)
            msg = f"'{product.name}' added to your cart."

        cart_count = sum(item.quantity for item in cart.items.all())

        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': msg,
                'cart_count': cart_count,
                'product_id': product.id,
                'stock': product.stock,
                'cart_quantity': cart_item.quantity,
            })

        messages.success(request, msg)
        return redirect('cart_view')


@login_required
def update_cart(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        action = request.POST.get('action')
        product = cart_item.product

        if action == 'increase':
            if not product.is_available:
                messages.error(request, f"'{product.name}' is currently unavailable.")
            elif product.stock <= 0:
                messages.error(request, f"'{product.name}' is currently out of stock.")
            elif cart_item.quantity >= product.stock:
                messages.error(request, f"Only {product.stock} unit(s) of '{product.name}' are available.")
            else:
                cart_item.quantity += 1
                cart_item.save(update_fields=['quantity'])
                messages.success(request, "Cart updated successfully.")

        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save(update_fields=['quantity'])
                messages.success(request, "Cart updated successfully.")
            else:
                product_name = cart_item.product.name
                cart_item.delete()
                messages.info(request, f"'{product_name}' was removed from cart.")

        return redirect('cart_view')


@login_required
def remove_from_cart(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        product_name = cart_item.product.name

        cart_item.delete()

        messages.success(request, f"'{product_name}' was removed from cart.")
        return redirect('cart_view')


@login_required
def buy_now(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, is_available=True)

        try:
            quantity = max(1, int(request.POST.get('quantity', 1)))
        except (TypeError, ValueError):
            quantity = 1

        if product.stock <= 0:
            return JsonResponse({
                'success': False,
                'message': 'This product is currently out of stock.',
                'stock': product.stock,
            }, status=400)

        if quantity > product.stock:
            return JsonResponse({
                'success': False,
                'message': f"Only {product.stock} unit(s) are available in stock.",
                'stock': product.stock,
            }, status=400)

        request.session['buy_now'] = {
            'product_id': product.id,
            'quantity': quantity,
        }
        request.session.modified = True

        checkout_url = reverse('checkout') + '?buy_now=1'
        return JsonResponse({'success': True, 'redirect_url': checkout_url})


def cart_context(request):
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_count = sum(item.quantity for item in cart.items.all())
        except Cart.DoesNotExist:
            cart_count = 0

    return {'cart_count': cart_count}