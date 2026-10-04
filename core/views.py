from django.shortcuts import render 
from django.db.models import Avg, Count, Sum,Q 
 
from products.models import Product, Category 
from core.models import Slider
from orders.models import OrderItem 
from products.utils import add_category_icons
 
 
def home(request): 
 
    # ========================================================= 
    # 1. FEATURED PRODUCTS 
    # ========================================================= 
    featured_products = ( 
        Product.objects 
        .filter( 
            is_featured=True, 
            is_available=True 
        ) 
        .annotate( 
            avg_rating=Avg('reviews__rating'), 
            review_count=Count( 
                'reviews', 
                distinct=True 
            ) 
        ) 
        .order_by('-created_at')[:8] 
    ) 
 
    # ========================================================= 
    # 2. NEW ARRIVALS 
    # ========================================================= 
    new_arrivals = ( 
        Product.objects 
        .filter( 
            is_available=True 
        ) 
        .annotate( 
            avg_rating=Avg('reviews__rating'), 
            review_count=Count( 
                'reviews', 
                distinct=True 
            ) 
        ) 
        .order_by('-created_at')[:8] 
    ) 
 
    # ========================================================= 
    # 3. BEST SELLERS 
    # 
    # Actual OrderItem quantity ke according products rank honge. 
    # 
    # Cancelled orders ko sales mein count nahi karenge. 
    # ========================================================= 
 
    best_selling_product_ids = ( 
        OrderItem.objects 
        .exclude( 
            order__status='Cancelled' 
        ) 
        .values('product') 
        .annotate( 
            total_sold=Sum('quantity') 
        ) 
        .order_by( 
            '-total_sold' 
        )[:8] 
    ) 
 
    # IDs ko list mein convert karna 
    best_seller_ids = [ 
        item['product'] 
        for item in best_selling_product_ids 
    ] 
 
    # Actual products fetch karna 
    best_sellers_queryset = ( 
        Product.objects 
        .filter( 
            id__in=best_seller_ids, 
            is_available=True 
        ) 
        .annotate( 
            avg_rating=Avg('reviews__rating'), 
            review_count=Count( 
                'reviews', 
                distinct=True 
            ) 
        ) 
    ) 
 
    # Database ka id__in order preserve nahi hota, 
    # isliye best-selling order manually restore kar rahe hain. 
    best_sellers_dict = { 
        product.id: product 
        for product in best_sellers_queryset 
    } 
 
    best_sellers = [ 
        best_sellers_dict[product_id] 
        for product_id in best_seller_ids 
        if product_id in best_sellers_dict 
    ] 
       

    categories = (
    Category.objects
    .annotate(
        product_count=Count(
            'products',
            filter=Q(
                products__is_available=True
            ),
            distinct=True
        )
    )
    .filter(
        product_count__gt=0
    )
    .order_by('name')
    )

    categories = add_category_icons(categories)
    sliders = (
        Slider.objects
        .filter(is_active=True)
        .order_by('display_order', 'id')
    )
   
    # ========================================================= 
    # 5. CURRENT USER WISHLIST 
    # 
    # Logged-in user ne jo products wishlist kiye hain, 
    # unke IDs homepage ke product cards mein heart status 
    # ke liye use honge. 
    # ========================================================= 
    user_wishlist_product_ids = set() 
 
    if request.user.is_authenticated: 
        user_wishlist_product_ids = set( 
            request.user.wishlist_items.values_list( 
                'product_id', 
                flat=True 
            ) 
        ) 
 
    # ========================================================= 
    # 6. CONTEXT 
    # 
    # Testimonials intentionally yahan nahi hain. 
    # Tumhare homepage testimonials static rahenge. 
    # ========================================================= 
    context = { 
        'featured_products': featured_products, 
        'new_arrivals': new_arrivals, 
        'best_sellers': best_sellers, 
        'categories': categories, 
        'user_wishlist_product_ids': user_wishlist_product_ids, 
        'sliders': sliders,

    } 
 
    # ========================================================= 
    # 7. RENDER HOME PAGE 
    # ========================================================= 
    return render( 
        request, 
        'client/home.html', 
        context 
    ) 