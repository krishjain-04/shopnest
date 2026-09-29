import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.urls import reverse

from django.http import HttpResponse
from products.models import Product
from cart.models import Cart
from .models import Address, Order, OrderItem
from .forms import AddressForm
from .invoice import send_invoice_email, generate_invoice_pdf


def get_product_selling_price(product):
    if (
        product.discount_price is not None
        and product.discount_price > 0
        and product.discount_price < product.price
    ):
        return product.discount_price

    return product.price


@login_required
def checkout_view(request):
    is_buy_now = request.GET.get('buy_now') == '1'
    buy_now = request.session.get('buy_now') if is_buy_now else None

    if is_buy_now and buy_now:
        product_id = buy_now.get('product_id')
        product = get_object_or_404(Product, id=product_id, is_available=True)

        try:
            quantity = int(buy_now.get('quantity', 1))
        except (TypeError, ValueError):
            quantity = 1

        if quantity < 1:
            quantity = 1

        if product.stock <= 0:
            request.session.pop('buy_now', None)
            request.session.modified = True
            messages.error(request, f"'{product.name}' is currently out of stock.")
            return redirect('product_detail', slug=product.slug)

        if quantity > product.stock:
            quantity = product.stock
            request.session['buy_now']['quantity'] = quantity
            request.session.modified = True
            messages.warning(
                request,
                f"Only {product.stock} unit(s) of '{product.name}' are available. Quantity has been adjusted."
            )

        unit_price = get_product_selling_price(product)
        total_price = unit_price * quantity

        buy_now_item = {
            'product': product,
            'quantity': quantity,
            'unit_price': unit_price,
            'total_price': total_price,
        }

        cart_items = []
        total_quantity = quantity
        grand_total = total_price
        checkout_type = 'buy_now'

    else:
        if 'buy_now' in request.session:
            request.session.pop('buy_now', None)
            request.session.modified = True

        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_items = list(
            cart.items.select_related('product', 'product__brand').all()
        )

        if not cart_items:
            messages.warning(
                request, "Your cart is empty. Please add items before checking out."
            )
            return redirect('cart_view')

        invalid_stock_items = []
        valid_cart_items = []

        for item in cart_items:
            product = item.product

            if not product.is_available:
                invalid_stock_items.append(f"'{product.name}' is currently unavailable.")
                continue

            if product.stock <= 0:
                invalid_stock_items.append(f"'{product.name}' is currently out of stock.")
                continue

            if item.quantity > product.stock:
                invalid_stock_items.append(
                    f"Only {product.stock} unit(s) of '{product.name}' are available. "
                    f"You currently have {item.quantity} in your cart."
                )
                continue

            valid_cart_items.append(item)

        if invalid_stock_items:
            for error_message in invalid_stock_items:
                messages.error(request, error_message)
            return redirect('cart_view')

        total_quantity = sum(item.quantity for item in valid_cart_items)
        grand_total = sum(
            get_product_selling_price(item.product) * item.quantity
            for item in valid_cart_items
        )
        buy_now_item = None
        checkout_type = 'cart'
        cart_items = valid_cart_items

    addresses = Address.objects.filter(user=request.user).order_by('-is_default', '-created_at')
    form = AddressForm()

    context = {
        'cart_items': cart_items,
        'buy_now_item': buy_now_item,
        'grand_total': grand_total,
        'total_quantity': total_quantity,
        'addresses': addresses,
        'form': form,
        'checkout_type': checkout_type,
    }

    return render(request, 'client/checkout.html', context)


@login_required
@transaction.atomic
def place_order_view(request):
    if request.method != 'POST':
        return redirect('checkout')

    selected_address_id = request.POST.get('selected_address')
    address = None

    if selected_address_id:
        address = get_object_or_404(Address, id=selected_address_id, user=request.user)
    else:
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user

            if address.is_default or not Address.objects.filter(user=request.user).exists():
                Address.objects.filter(user=request.user).update(is_default=False)
                address.is_default = True

            address.save()
        else:
            messages.error(request, "Please select or fill in a valid shipping address.")
            return redirect('checkout')

    buy_now = request.session.get('buy_now')

    if buy_now:
        product = get_object_or_404(Product, id=buy_now.get('product_id'), is_available=True)

        try:
            quantity = int(buy_now.get('quantity', 1))
        except (TypeError, ValueError):
            quantity = 1

        if quantity < 1:
            quantity = 1

        if product.stock <= 0:
            request.session.pop('buy_now', None)
            request.session.modified = True
            messages.error(request, f"'{product.name}' is currently out of stock.")
            return redirect('product_detail', slug=product.slug)

        if quantity > product.stock:
            request.session['buy_now']['quantity'] = product.stock
            request.session.modified = True
            messages.error(request, f"Only {product.stock} unit(s) of '{product.name}' are available.")
            return redirect(f"{reverse('checkout')}?buy_now=1")

        current_price = get_product_selling_price(product)
        grand_total = current_price * quantity
        generated_order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"

        order = Order.objects.create(
            user=request.user,
            address=address,
            total_amount=grand_total,
            status='Pending',
            order_id=generated_order_id,
            payment_method=request.POST.get('payment_method', 'Cash on Delivery'),
            payment_status='Pending'
        )

        OrderItem.objects.create(
            order=order,
            product=product,
            price=current_price,
            quantity=quantity,
            subtotal=grand_total
        )

        product.stock -= quantity
        product.save(update_fields=['stock'])

       

        request.session.pop('buy_now', None)
        request.session.modified = True

        return redirect('order_success', order_id=order.order_id)

    cart = get_object_or_404(Cart, user=request.user)
    cart_items = list(cart.items.select_related('product', 'product__brand').all())

    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return redirect('checkout')

    for item in cart_items:
        product = item.product

        if not product.is_available:
            messages.error(request, f"'{product.name}' is currently unavailable.")
            return redirect('cart_view')

        if product.stock <= 0:
            messages.error(request, f"'{product.name}' is currently out of stock.")
            return redirect('cart_view')

        if item.quantity > product.stock:
            messages.error(
                request,
                f"Only {product.stock} unit(s) of '{product.name}' are available. Please update your cart quantity."
            )
            return redirect('cart_view')

    grand_total = sum(get_product_selling_price(item.product) * item.quantity for item in cart_items)
    generated_order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"

    order = Order.objects.create(
        user=request.user,
        address=address,
        total_amount=grand_total,
        status='Pending',
        order_id=generated_order_id,
        payment_method=request.POST.get('payment_method', 'Cash on Delivery'),
        payment_status='Pending'
    )

    for item in cart_items:
        product = item.product
        current_price = get_product_selling_price(product)
        subtotal_price = current_price * item.quantity

        OrderItem.objects.create(
            order=order,
            product=product,
            price=current_price,
            quantity=item.quantity,
            subtotal=subtotal_price
        )

        product.stock -= item.quantity
        product.save(update_fields=['stock'])

   

    cart.items.all().delete()

    return redirect('order_success', order_id=order.order_id)


@login_required
def order_success_view(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    return render(request, 'client/order_success.html', {'order': order})


@login_required
def my_orders_view(request):
    orders_list = Order.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(orders_list, 5)
    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)

    return render(request, 'client/my_orders.html', {'orders': orders})


@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    items = order.items.select_related('product').all()

    statuses = ['Pending', 'Processing', 'Shipped', 'Delivered']
    current_status_index = statuses.index(order.status) if order.status in statuses else -1
    can_cancel = order.status in ['Pending', 'Processing']

    context = {
        'order': order,
        'items': items,
        'statuses': statuses,
        'current_status_index': current_status_index,
        'can_cancel': can_cancel,
    }

    return render(request, 'client/order_detail.html', context)


@login_required
@transaction.atomic
def cancel_order_view(request, order_id):
    if request.method != 'POST':
        return redirect('order_detail', order_id=order_id)

    order = get_object_or_404(Order, order_id=order_id, user=request.user)

    if order.status not in ['Pending', 'Processing']:
        messages.error(
            request,
            f"This order cannot be cancelled because its current status is {order.status}."
        )
        return redirect('order_detail', order_id=order.order_id)

    order_items = order.items.select_related('product').all()
    for item in order_items:
        product = item.product
        product.stock += item.quantity
        product.save(update_fields=['stock'])

    order.status = 'Cancelled'
    order.save(update_fields=['status'])

    messages.success(request, f"Order #{order.order_id} has been cancelled successfully.")
    return redirect('order_detail', order_id=order.order_id)


@login_required
def address_list_view(request):
    addresses = Address.objects.filter(user=request.user).order_by('-is_default', '-created_at')
    form = AddressForm()

    return render(
        request,
        'client/address_list.html',
        {'addresses': addresses, 'form': form}
    )


@login_required
def add_address_view(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user

            if address.is_default or not Address.objects.filter(user=request.user).exists():
                Address.objects.filter(user=request.user).update(is_default=False)
                address.is_default = True

            address.save()
            messages.success(request, "Address added successfully.")

    return redirect('address_list')


@login_required
def edit_address_view(request, pk):
    address = get_object_or_404(Address, id=pk, user=request.user)

    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            updated_address = form.save(commit=False)

            if updated_address.is_default:
                Address.objects.filter(user=request.user).exclude(id=address.id).update(is_default=False)

            updated_address.save()
            messages.success(request, "Address updated successfully.")
            return redirect('address_list')
    else:
        form = AddressForm(instance=address)

    return render(
        request,
        'client/edit_address.html',
        {'form': form, 'address': address}
    )


@login_required
def delete_address_view(request, pk):
    address = get_object_or_404(Address, id=pk, user=request.user)

    if request.method == 'POST':
        was_default = address.is_default
        address.delete()

        if was_default:
            first_addr = Address.objects.filter(user=request.user).first()
            if first_addr:
                first_addr.is_default = True
                first_addr.save()

        messages.success(request, "Address deleted successfully.")

    return redirect('address_list')


@login_required
def set_default_address_view(request, pk):
    address = get_object_or_404(Address, id=pk, user=request.user)

    Address.objects.filter(user=request.user).update(is_default=False)
    address.is_default = True
    address.save()

    messages.success(request, "Default address updated.")
    return redirect('address_list')


@login_required
def download_invoice_view(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    pdf = generate_invoice_pdf(order)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.order_id}.pdf"'
    return response