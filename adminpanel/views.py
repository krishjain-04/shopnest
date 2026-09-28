from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from .models import AdminUser
from django.utils.text import slugify
from products.models import Category,SubCategory, ThirdCategory, Brand,Product,ProductImage,Wishlist
from orders.models import Order, OrderItem
from orders.invoice import generate_invoice_pdf
from django.contrib.auth.models import User
from cart.models import Cart
from django.db.models import Sum, Count
from django.http import HttpResponse, JsonResponse




def admin_login(request):

    if 'admin_id' in request.session:
        return redirect('admin_dashboard')

    error_message =""
    if request.method =="POST":
        u_name = request.POST.get('username')
        p_pass = request.POST.get('password')

        try:
            admin=AdminUser.objects.get(username=u_name,password=p_pass)

            request.session['admin_id']=admin.id
            request.session['admin_username']=admin.username

            return redirect('admin_dashboard')
        except AdminUser.DoesNotExist:
            error_message="invalid username or password!"


    return render(request,'adminpanel/login.html',{'error':error_message})


def admin_logout(request):
    if 'admin_id' in request.session:
        del request.session['admin_id']
        del request.session['admin_username']
    return redirect('admin_login')



def admin_dashboard(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')

    # Session se admin name nikalna
    admin_name = request.session.get('admin_username', 'Admin')

    # Counts
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    total_orders = Order.objects.count()

    # iexact se status lowercase ho ya uppercase, exact match ho jayega
    pending_orders = Order.objects.filter(status__iexact='Pending').count()
    delivered_orders = Order.objects.filter(status__iexact='Delivered').count()
    cancelled_orders = Order.objects.filter(status__iexact='Cancelled').count()

    # Revenue (Sirf Delivered Orders ka sum)
    revenue_data = Order.objects.filter(status__iexact='Delivered').aggregate(total=Sum('total_amount'))
    total_revenue = revenue_data['total'] if revenue_data['total'] is not None else 0.00

    # Cart & Wishlist Totals
    total_cart_items = Cart.objects.count()
    total_wishlist_items = Wishlist.objects.count()

    # Top 5 Wishlisted Products
    top_wishlisted = Product.objects.annotate(
        wish_count=Count('wishlisted_by')
    ).order_by('-wish_count')[:5]

    context = {
        'admin_name': admin_name, # Added admin_name
        'total_products': total_products,
        'total_categories': total_categories,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'delivered_orders': delivered_orders,
        'cancelled_orders': cancelled_orders,
        'total_revenue': total_revenue,
        'total_cart_items': total_cart_items,
        'total_wishlist_items': total_wishlist_items,
        'top_wishlisted': top_wishlisted,
    }
    return render(request, 'adminpanel/dashboard.html', context)



def category_list(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')

    categories=Category.objects.all().order_by('-created_at')
    return render(request,'adminpanel/categories.html',{'categories':categories})


def add_category(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')

    if request.method == "POST":
        name = request.POST.get('name')
        if name:
            slug = slugify(name)
            # Automatic Slug handling
            Category.objects.create(name=name, slug=slug)
            return redirect('admin_categories')

    return render(request, 'adminpanel/add_category.html')

def delete_category(request,id):
    if 'admin_id' not in request.session:
        return redirect('admin_login')

    try:
        category=Category.objects.get(id=id)
        category.delete()
    except Category.DoesNotExist:
        pass

    return redirect('admin_categories')


def subcategory_list(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')
    subcategories=SubCategory.objects.all().order_by('-created_at')
    return render(request,'adminpanel/subcategories.html',{"subcategories":subcategories})

def add_subcategory(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')
    if request.method=="POST":
        name=request.POST.get('name')
        category_id=request.POST.get('category')

        if name and category_id:
            slug=slugify(name)

            SubCategory.objects.create(name=name,slug=slug,category_id=category_id)
            return redirect('admin_subcategories')

    categories=Category.objects.all()
    return render(request,'adminpanel/add_subcategory.html',{'categories':categories})


def delete_subcategory(request, id):
    if 'admin_id' not in request.session:
        return redirect('admin_login')

    try:
        subcat = SubCategory.objects.get(id=id)
        subcat.delete()
    except SubCategory.DoesNotExist:
        pass

    return redirect('admin_subcategories')




def thirdcategory_list(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')
        
    thirdcategories = ThirdCategory.objects.all().order_by('-created_at')
    return render(request, 'adminpanel/thirdcategories.html', {'thirdcategories': thirdcategories})


# 2. ADD THIRDCATEGORY
def add_thirdcategory(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')

    if request.method == "POST":
        name = request.POST.get('name')
        subcategory_id = request.POST.get('subcategory') # Dropdown se SubCategory ID aayegi

        if name and subcategory_id:
            slug = slugify(name)
            
            # ThirdCategory table me save kar rahe hain
            ThirdCategory.objects.create(
                name=name,
                slug=slug,
                subcategory_id=subcategory_id # Foreign Key Link
            )
            return redirect('admin_thirdcategories')

    # Dropdown me dikhane ke liye saari SubCategories bhej rahe hain
    subcategories = SubCategory.objects.all()
    return render(request, 'adminpanel/add_thirdcategory.html', {'subcategories': subcategories})



def delete_thirdcategory(request, id):
    if 'admin_id' not in request.session:
        return redirect('admin_login')

    try:
        thirdcat = ThirdCategory.objects.get(id=id)
        thirdcat.delete()
    except ThirdCategory.DoesNotExist:
        pass

    return redirect('admin_thirdcategories')



def brand_list(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')
        
    brands = Brand.objects.all().order_by('-created_at')
    return render(request, 'adminpanel/brands.html', {'brands': brands})


def add_brand(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')

    if request.method == "POST":
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        logo = request.FILES.get('logo')

        if name and category_id:
            slug = slugify(name)

            Brand.objects.create(
                name=name,
                slug=slug,
                category_id=category_id,
                logo=logo
            )

            return redirect('admin_brands')

    categories = Category.objects.all()

    return render(
        request,
        'adminpanel/add_brand.html',
        {'categories': categories}
    )


def delete_brand(request, id):
    if 'admin_id' not in request.session:
        return redirect('admin_login')

    try:
        brand = Brand.objects.get(id=id)
        brand.delete()
    except Brand.DoesNotExist:
        pass

    return redirect('admin_brands')

def edit_brand(request, id):
    if 'admin_id' not in request.session:
        return redirect('admin_login')

    brand = get_object_or_404(Brand, id=id)

    if request.method == "POST":
        name = request.POST.get('name')
        logo = request.FILES.get('logo')
        category_id = request.POST.get('category')

        if name and category_id:
            brand.name = name
            brand.slug = slugify(name)
            brand.category_id = category_id

            if logo:
                brand.logo = logo

            brand.save()

            return redirect('admin_brands')

    context = {
        'brand': brand,
        'categories': Category.objects.all()
    }

    return render(request, 'adminpanel/edit_brand.html', context)

def get_brands(request):
    category_id = request.GET.get('category_id')

    brands = Brand.objects.filter(
        category_id=category_id
    ).values('id', 'name')

    return JsonResponse(list(brands), safe=False)

def product_list(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')
        
    products = Product.objects.all().order_by('-created_at')

    
    search = request.GET.get('search')
    if search:
        products = products.filter(name__icontains=search)

    
    cat_id = request.GET.get('category')
    selected_cat = int(cat_id) if cat_id else None
    
    if selected_cat:
        products = products.filter(category_id=selected_cat)

    context = {
        'products': products,
        'categories': Category.objects.all(),
        'search': search or '',
        'selected_cat': selected_cat
    }
    return render(request, 'adminpanel/products.html', context)


def add_product(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')

    if request.method == "POST":
        # Form Data Fetching
        name = request.POST.get('name')
        price = request.POST.get('price')
        discount_price = request.POST.get('discount_price') or None # Optional field
        stock = request.POST.get('stock') or 0
        short_desc = request.POST.get('short_description')
        desc = request.POST.get('description')
        
        # Dropdowns Se IDs (Foreign Keys)
        category_id = request.POST.get('category')
        subcategory_id = request.POST.get('subcategory')
        thirdcategory_id = request.POST.get('thirdcategory')
        brand_id = request.POST.get('brand')
        
        
        main_image = request.FILES.get('main_image')

        if name and price and category_id and subcategory_id and thirdcategory_id and brand_id:
            slug = slugify(name)

            # Database me Product Save kar rahe hain
            Product.objects.create(
                name=name,
                slug=slug,
                price=price,
                discount_price=discount_price,
                stock=stock,
                short_description=short_desc,
                description=desc,
                category_id=category_id,
                subcategory_id=subcategory_id,
                thirdcategory_id=thirdcategory_id,
                brand_id=brand_id,
                main_image=main_image
            )

            return redirect('admin_products')

    
    context = {
        'categories': Category.objects.all(),
        'subcategories': SubCategory.objects.all(),
        'thirdcategories': ThirdCategory.objects.all(),
        'brands': Brand.objects.all(),
    }
    return render(request, 'adminpanel/add_product.html', context)


def edit_product(request, id):
    if 'admin_id' not in request.session:
        return redirect('admin_login')

    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        product.name = request.POST.get('name')
        product.slug = slugify(product.name)
        product.price = request.POST.get('price')
        product.discount_price = request.POST.get('discount_price') or None
        product.stock = request.POST.get('stock') or 0
        product.short_description = request.POST.get('short_description')
        product.description = request.POST.get('description')
        
        product.category_id = request.POST.get('category')
        product.subcategory_id = request.POST.get('subcategory')
        product.thirdcategory_id = request.POST.get('thirdcategory')
        product.brand_id = request.POST.get('brand')

        # Main Single Image Update
        if request.FILES.get('main_image'):
            product.main_image = request.FILES.get('main_image')

        product.save()

        # Extra Gallery Images Upload Logic 
        extra_images = request.FILES.getlist('extra_images')
        for img in extra_images:
            ProductImage.objects.create(product=product, image=img)

        return redirect('edit_product', id=product.id)

    context = {
        'product': product,
        'categories': Category.objects.all(),
        'subcategories': SubCategory.objects.all(),
        'thirdcategories': ThirdCategory.objects.all(),
        'brands': Brand.objects.all(),
    }
    return render(request, 'adminpanel/edit_product.html', context)



def delete_product_image(request, id):
    if 'admin_id' not in request.session:
        return redirect('admin_login')

    img_obj = get_object_or_404(ProductImage, id=id)
    product_id = img_obj.product.id
    
    
    img_obj.delete()

    return redirect('edit_product', id=product_id)


def delete_product(request, id):
    if 'admin_id' not in request.session:
        return redirect('admin_login')

    try:
        product = Product.objects.get(id=id)
        product.delete()
    except Product.DoesNotExist:
        pass

    return redirect('admin_products')





# 2. ALL ORDERS LIST
def order_list(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')
        
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'adminpanel/orders.html', {'orders': orders})


# 3. ORDER DETAIL VIEW (Address & Items)
def order_detail(request, id):
    if 'admin_id' not in request.session:
        return redirect('admin_login')
        
    order = get_object_or_404(Order, id=id)

    items = order.items.all()
    
    return render(request, 'adminpanel/order_detail.html', {'order': order, 'items': items})


# 4. UPDATE ORDER STATUS & PAYMENT STATUS
def update_order_status(request, id):
    if 'admin_id' not in request.session:
        return redirect('admin_login')

    if request.method == "POST":
        new_status = request.POST.get('status')
        new_payment_status = request.POST.get('payment_status')
        
        order = get_object_or_404(Order, id=id)
        
        if new_status:
            order.status = new_status
        if new_payment_status:
            order.payment_status = new_payment_status
            
        order.save()
        
    return redirect('admin_order_detail', id=id)



def order_list(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')
        
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'adminpanel/orders.html', {'orders': orders})


# ORDER DETAIL VIEW (Address & Items)
def order_detail(request, id):
    if 'admin_id' not in request.session:
        return redirect('admin_login')
        
    order = get_object_or_404(Order, id=id)

    items = order.items.all()
    
    return render(request, 'adminpanel/order_detail.html', {'order': order, 'items': items})


# UPDATE ORDER STATUS & PAYMENT STATUS
def update_order_status(request, id):
    if 'admin_id' not in request.session:
        return redirect('admin_login')

    if request.method == "POST":
        new_status = request.POST.get('status')
        new_payment_status = request.POST.get('payment_status')
        
        order = get_object_or_404(Order, id=id)
        
        if new_status:
            order.status = new_status
        if new_payment_status:
            order.payment_status = new_payment_status
            
        order.save()
        
    return redirect('admin_order_detail', id=id)







def user_list(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')
        
    
    users = User.objects.filter(is_superuser=False).order_by('-date_joined')
    return render(request, 'adminpanel/users.html', {'users': users})



def user_detail(request, id):
    if 'admin_id' not in request.session:
        return redirect('admin_login')
        
    customer = get_object_or_404(User, id=id)
    
    
    profile = getattr(customer, 'profile', None)
    
    
    user_orders = Order.objects.filter(user=customer).order_by('-created_at')

    context = {
        'customer': customer,
        'profile': profile,
        'orders': user_orders,
        'total_orders_count': user_orders.count()
    }
    return render(request, 'adminpanel/user_detail.html', context)


# 3. TOGGLE USER ACTIVE/BLOCK STATUS
def toggle_user_status(request, id):
    if 'admin_id' not in request.session:
        return redirect('admin_login')

    customer = get_object_or_404(User, id=id)
    
    
    customer.is_active = not customer.is_active
    customer.save()

    return redirect('admin_user_detail',id=id)


def admin_download_invoice(request, id):
    if 'admin_id' not in request.session:
        return redirect('admin_login')

    order = get_object_or_404(Order, id=id)
    pdf = generate_invoice_pdf(order)
    filename = order.order_id if order.order_id else f"order_{order.id}"
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{filename}.pdf"'
    return response

def get_subcategories(request):
    category_id = request.GET.get('category_id')

    subcategories = SubCategory.objects.filter(
        category_id=category_id
    ).values('id', 'name')

    return JsonResponse(list(subcategories), safe=False)


def get_thirdcategories(request):
    subcategory_id = request.GET.get('subcategory_id')

    thirdcategories = ThirdCategory.objects.filter(
        subcategory_id=subcategory_id
    ).values('id', 'name')

    return JsonResponse(list(thirdcategories), safe=False)