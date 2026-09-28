from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import (
    Product,
    Category,
    SubCategory,
    ThirdCategory,
    Brand,
    Review,
    Wishlist,
)

from .utils import (
    add_category_icons,
    add_subcategory_icons,
    add_thirdcategory_icons,
)


def get_filter_parameters(request):
    return {
        'selected_categories': [
            int(x) for x in request.GET.getlist('category')
            if x.isdigit()
        ],
        'selected_subcategories': [
            int(x) for x in request.GET.getlist('subcategory')
            if x.isdigit()
        ],
        'selected_thirdcategories': [
            int(x) for x in request.GET.getlist('thirdcategory')
            if x.isdigit()
        ],
        'selected_brands': [
            int(x) for x in request.GET.getlist('brand')
            if x.isdigit()
        ],
        'min_price': request.GET.get('min_price', '').strip(),
        'max_price': request.GET.get('max_price', '').strip(),
        'rating_filter': request.GET.get('rating', '').strip(),
        'in_stock_only': request.GET.get('in_stock'),
        'sort': request.GET.get('sort', ''),
    }


def apply_product_filters(products, request):
    filters = get_filter_parameters(request)

    if filters['selected_categories']:
        products = products.filter(
            category__id__in=filters['selected_categories']
        )

    if filters['selected_subcategories']:
        products = products.filter(
            subcategory__id__in=filters['selected_subcategories']
        )

    if filters['selected_thirdcategories']:
        products = products.filter(
            thirdcategory__id__in=filters['selected_thirdcategories']
        )

    if filters['selected_brands']:
        products = products.filter(
            brand__id__in=filters['selected_brands']
        )

    if filters['min_price']:
        try:
            products = products.filter(
                price__gte=float(filters['min_price'])
            )
        except (ValueError, TypeError):
            pass

    if filters['max_price']:
        try:
            products = products.filter(
                price__lte=float(filters['max_price'])
            )
        except (ValueError, TypeError):
            pass

    if filters['rating_filter']:
        try:
            products = products.filter(
                avg_rating__gte=float(filters['rating_filter'])
            )
        except (ValueError, TypeError):
            pass

    if filters['in_stock_only'] == '1':
        products = products.filter(stock__gt=0)

    sort_options = {
        'price_asc': 'price',
        'price_desc': '-price',
        'newest': '-created_at',
        'rating': '-avg_rating',
    }

    products = products.order_by(
        sort_options.get(filters['sort'], '-id')
    )

    return products, filters


def get_filter_sidebar_data():
    categories = (
        Category.objects
        .annotate(
            product_count=Count(
                'products',
                filter=Q(products__is_available=True)
            )
        )
        .filter(product_count__gt=0)
    )

    subcategories = (
        SubCategory.objects
        .annotate(
            product_count=Count(
                'products',
                filter=Q(products__is_available=True)
            )
        )
        .filter(product_count__gt=0)
    )

    thirdcategories = (
        ThirdCategory.objects
        .annotate(
            product_count=Count(
                'products',
                filter=Q(products__is_available=True)
            )
        )
        .filter(product_count__gt=0)
    )

    brands = (
        Brand.objects
        .annotate(
            product_count=Count(
                'products',
                filter=Q(products__is_available=True)
            )
        )
        .filter(product_count__gt=0)
    )

    return categories, subcategories, thirdcategories, brands


def get_wishlist_product_ids(request):
    if not request.user.is_authenticated:
        return []

    return list(
        Wishlist.objects
        .filter(user=request.user)
        .values_list('product_id', flat=True)
    )


def get_product_queryset():
    return (
        Product.objects
        .filter(is_available=True)
        .select_related(
            'category',
            'subcategory',
            'thirdcategory',
            'brand'
        )
        .annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        )
    )


def product_list(request):
    query = request.GET.get('q', '').strip()

    products = get_product_queryset()

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(short_description__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__name__icontains=query) |
            Q(category__name__icontains=query) |
            Q(subcategory__name__icontains=query) |
            Q(thirdcategory__name__icontains=query)
        )

    products, filters = apply_product_filters(
        products,
        request
    )

    categories, subcategories, thirdcategories, brands = (
        get_filter_sidebar_data()
    )

    get_params = request.GET.copy()
    get_params.pop('page', None)
    query_string = get_params.urlencode()

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(
        request.GET.get('page')
    )

    user_wishlist_product_ids = get_wishlist_product_ids(request)

    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'query': query,

        'categories': categories,
        'subcategories': subcategories,
        'thirdcategories': thirdcategories,
        'brands': brands,

        **filters,

        'query_string': query_string,

        'user_wishlist_product_ids': user_wishlist_product_ids,

        'has_active_filters': bool(
            filters['selected_categories']
            or filters['selected_subcategories']
            or filters['selected_thirdcategories']
            or filters['selected_brands']
            or filters['min_price']
            or filters['max_price']
            or filters['rating_filter']
            or filters['in_stock_only']
            or query
        ),
    }

    return render(
        request,
        'client/product_list.html',
        context
    )


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects
        .select_related(
            'category',
            'subcategory',
            'thirdcategory',
            'brand'
        )
        .prefetch_related(
            'images',
            'reviews'
        )
        .annotate(
            average_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ),
        slug=slug
    )

    if request.method == 'POST':
        Review.objects.create(
            product=product,
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            rating=request.POST.get('rating'),
            review=request.POST.get('review')
        )

        return redirect(
            'product_detail',
            slug=product.slug
        )

    related_products = (
        Product.objects
        .filter(
            category=product.category,
            is_available=True
        )
        .exclude(id=product.id)
        .select_related('brand')
        .annotate(
            average_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        )
        .order_by('-created_at')[:4]
    )

    is_wishlisted = False

    if request.user.is_authenticated:
        is_wishlisted = Wishlist.objects.filter(
            user=request.user,
            product=product
        ).exists()

    return render(
        request,
        'client/product_detail.html',
        {
            'product': product,
            'related_products': related_products,
            'is_wishlisted': is_wishlisted,
        }
    )


def search_products(request):
    query = request.GET.get('q', '').strip()

    products = get_product_queryset()

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(short_description__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__name__icontains=query) |
            Q(category__name__icontains=query) |
            Q(subcategory__name__icontains=query) |
            Q(thirdcategory__name__icontains=query)
        )

    products, filters = apply_product_filters(
        products,
        request
    )

    categories, subcategories, thirdcategories, brands = (
        get_filter_sidebar_data()
    )

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(
        request.GET.get('page')
    )

    user_wishlist_product_ids = get_wishlist_product_ids(request)

    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'query': query,

        'categories': categories,
        'subcategories': subcategories,
        'thirdcategories': thirdcategories,
        'brands': brands,

        **filters,

        'user_wishlist_product_ids': user_wishlist_product_ids,
    }

    return render(
        request,
        'client/search_results.html',
        context
    )


def all_categories(request):
    categories = add_category_icons(
        Category.objects.all()
    )

    brands = Brand.objects.all()

    return render(
        request,
        'client/all_categories.html',
        {
            'categories': categories,
            'brands': brands,
        }
    )


def category_detail(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug
    )

    subcategories = add_subcategory_icons(
        category.subcategories.all()
    )

    return render(
        request,
        'client/category_detail.html',
        {
            'category': category,
            'subcategories': subcategories,
        }
    )


def subcategory_detail(
    request,
    category_slug,
    subcategory_slug
):
    category = get_object_or_404(
        Category,
        slug=category_slug
    )

    subcategory = get_object_or_404(
        SubCategory,
        slug=subcategory_slug
    )

    thirdcategories = add_thirdcategory_icons(
        subcategory.thirdcategories.all()
    )

    return render(
        request,
        'client/subcategory_detail.html',
        {
            'category': category,
            'subcategory': subcategory,
            'thirdcategories': thirdcategories,
        }
    )


def thirdcategory_detail(
    request,
    category_slug,
    subcategory_slug,
    third_slug
):
    thirdcategory = get_object_or_404(
        ThirdCategory,
        slug=third_slug
    )

    products = (
        Product.objects
        .filter(
            thirdcategory=thirdcategory,
            is_available=True
        )
        .select_related(
            'category',
            'subcategory',
            'thirdcategory',
            'brand'
        )
        .annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        )
        .order_by('-created_at')
    )

    user_wishlist_product_ids = get_wishlist_product_ids(request)

    return render(
        request,
        'client/thirdcategory_detail.html',
        {
            'thirdcategory': thirdcategory,
            'products': products,
            'user_wishlist_product_ids': user_wishlist_product_ids,
        }
    )


@login_required
def wishlist_view(request):
    wishlist_items = (
        Wishlist.objects
        .filter(user=request.user)
        .select_related(
            'product',
            'product__category',
            'product__subcategory',
            'product__thirdcategory',
            'product__brand'
        )
    )

    return render(
        request,
        'client/wishlist.html',
        {
            'wishlist_items': wishlist_items
        }
    )


@login_required
def toggle_wishlist(request, product_id):
    if request.method != 'POST':
        return redirect(
            request.META.get(
                'HTTP_REFERER',
                'wishlist'
            )
        )

    product = get_object_or_404(
        Product,
        id=product_id
    )

    wishlist_item = Wishlist.objects.filter(
        user=request.user,
        product=product
    )

    if wishlist_item.exists():
        wishlist_item.delete()
        added = False
    else:
        Wishlist.objects.create(
            user=request.user,
            product=product
        )
        added = True

    total_count = Wishlist.objects.filter(
        user=request.user
    ).count()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'added': added,
            'wishlist_count': total_count,
            'product_id': product.id,
        })

    return redirect(
        request.META.get(
            'HTTP_REFERER',
            'wishlist'
        )
    )


@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id
    )

    Wishlist.objects.filter(
        user=request.user,
        product=product
    ).delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        wishlist_count = Wishlist.objects.filter(
            user=request.user
        ).count()

        return JsonResponse({
            'removed': True,
            'wishlist_count': wishlist_count,
            'product_id': product.id,
        })

    return redirect(
        request.META.get(
            'HTTP_REFERER',
            'wishlist_detail'
        )
    )