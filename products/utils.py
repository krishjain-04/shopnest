# ==========================================
# CATEGORY ICONS
# ==========================================

CATEGORY_ICONS = {

    # Electronics
    'electronics': 'fa-solid fa-tv',

    # Fashion
    'fashion': 'fa-solid fa-shirt',
    'clothing': 'fa-solid fa-shirt',
    'footwear': 'fa-solid fa-shoe-prints',

    # Home & Kitchen
    'home & kitchen': 'fa-solid fa-house',
    'home': 'fa-solid fa-house',

    # Furniture
    'furniture': 'fa-solid fa-couch',

    # Books
    'books': 'fa-solid fa-book',
    'book': 'fa-solid fa-book',

    # Beauty & Health
    'beauty': 'fa-solid fa-sparkles',
    'health': 'fa-solid fa-heart-pulse',

    # Sports & Toys
    'sports': 'fa-solid fa-dumbbell',
    'toys': 'fa-solid fa-gamepad',

    # Grocery
    'groceries': 'fa-solid fa-basket-shopping',
    'grocery': 'fa-solid fa-basket-shopping',

    # Automotive
    'automotive': 'fa-solid fa-car',
    'cars': 'fa-solid fa-car',

    # Jewellery
    'jewellery': 'fa-solid fa-gem',
    'jewelry': 'fa-solid fa-gem',

    # Accessories
    'accessories': 'fa-solid fa-bag-shopping',
}


# ==========================================
# SUBCATEGORY ICONS
# ==========================================

SUBCATEGORY_ICONS = {

    # Electronics
    'mobiles': 'fa-solid fa-mobile-screen-button',
    'mobile': 'fa-solid fa-mobile-screen-button',

    'laptops': 'fa-solid fa-laptop',
    'laptop': 'fa-solid fa-laptop',

    'tablets': 'fa-solid fa-tablet-screen-button',
    'tablet': 'fa-solid fa-tablet-screen-button',

    'televisions': 'fa-solid fa-tv',
    'television': 'fa-solid fa-tv',
    'tv': 'fa-solid fa-tv',

    'headphones': 'fa-solid fa-headphones',
    'earphones': 'fa-solid fa-headphones',

    'cameras': 'fa-solid fa-camera',
    'camera': 'fa-solid fa-camera',

    'smartwatches': 'fa-solid fa-clock',
    'smart watches': 'fa-solid fa-clock',
    'smartwatch': 'fa-solid fa-clock',

    # Fashion
    'mens clothing': 'fa-solid fa-shirt',
    "men's clothing": 'fa-solid fa-shirt',
    'womens clothing': 'fa-solid fa-shirt',
    "women's clothing": 'fa-solid fa-shirt',
    'clothing': 'fa-solid fa-shirt',

    'footwear': 'fa-solid fa-shoe-prints',
    'shoes': 'fa-solid fa-shoe-prints',

    'bags': 'fa-solid fa-bag-shopping',
    'handbags': 'fa-solid fa-bag-shopping',

    'watches': 'fa-solid fa-clock',

    'accessories': 'fa-solid fa-gem',

    # Home & Kitchen
    'furniture': 'fa-solid fa-couch',

    'kitchen appliances': 'fa-solid fa-kitchen-set',
    'appliances': 'fa-solid fa-kitchen-set',

    'home decor': 'fa-solid fa-house',
    'decor': 'fa-solid fa-house',

    # Books
    'books': 'fa-solid fa-book',

    # Beauty
    'makeup': 'fa-solid fa-wand-magic-sparkles',
    'skincare': 'fa-solid fa-spa',

    # Sports
    'sports': 'fa-solid fa-dumbbell',
    'fitness': 'fa-solid fa-dumbbell',

    # Automotive
    'cars': 'fa-solid fa-car',
    'car': 'fa-solid fa-car',
    'bike': 'fa-solid fa-motorcycle',
    'bikes': 'fa-solid fa-motorcycle',
}



# ==========================================
# THIRD CATEGORY ICONS
# ==========================================

THIRDCATEGORY_ICONS = {

    # Mobiles
    'android': 'fa-solid fa-mobile-screen-button',
    'android phone': 'fa-solid fa-mobile-screen-button',

    'iphones': 'fa-brands fa-apple',
    'iphone': 'fa-brands fa-apple',

    'feature phones': 'fa-solid fa-mobile-screen',
    'gaming phones': 'fa-solid fa-gamepad',

    # Laptops
    'gaming laptops': 'fa-solid fa-gamepad',
    'gaming laptop': 'fa-solid fa-gamepad',

    'business laptops': 'fa-solid fa-briefcase',
    'business laptop': 'fa-solid fa-briefcase',

    'student laptops': 'fa-solid fa-graduation-cap',
    'student laptop': 'fa-solid fa-graduation-cap',

    'ultrabooks': 'fa-solid fa-laptop',
    'ultrabook': 'fa-solid fa-laptop',

    # Footwear
    'sports shoes': 'fa-solid fa-person-running',
    'sports shoe': 'fa-solid fa-person-running',

    'casual shoes': 'fa-solid fa-shoe-prints',
    'casual shoe': 'fa-solid fa-shoe-prints',

    'formal shoes': 'fa-solid fa-shoe-prints',
    'formal shoe': 'fa-solid fa-shoe-prints',

    # Men's Clothing
    'jeans': 'fa-solid fa-jeans',
    'shirts': 'fa-solid fa-shirt',
    't-shirts': 'fa-solid fa-shirt',
    't shirts': 'fa-solid fa-shirt',

    # Kitchen
    'microwave ovens': 'fa-solid fa-microwave',
    'microwave oven': 'fa-solid fa-microwave',

    'refrigerators': 'fa-solid fa-temperature-low',
    'refrigerator': 'fa-solid fa-temperature-low',

    # Furniture
    'dining tables': 'fa-solid fa-table',
    'dining table': 'fa-solid fa-table',

    'sofas': 'fa-solid fa-couch',
    'sofa': 'fa-solid fa-couch',

    'beds': 'fa-solid fa-bed',
    'bed': 'fa-solid fa-bed',

    # Books
    'fiction': 'fa-solid fa-book-open',
    'non fiction': 'fa-solid fa-book',
    'non-fiction': 'fa-solid fa-book',

}


def add_thirdcategory_icons(thirdcategories):

    for thirdcategory in thirdcategories:

        thirdcategory.category_icon = THIRDCATEGORY_ICONS.get(
            thirdcategory.name.strip().lower(),
            'fa-solid fa-tags'
        )

    return thirdcategories

# ==========================================
# ADD CATEGORY ICONS
# ==========================================

def add_category_icons(categories):

    for category in categories:

        category.category_icon = CATEGORY_ICONS.get(
            category.name.strip().lower(),
            'fa-solid fa-layer-group'
        )

    return categories


# ==========================================
# ADD SUBCATEGORY ICONS
# ==========================================

def add_subcategory_icons(subcategories):

    for subcategory in subcategories:

        subcategory.category_icon = SUBCATEGORY_ICONS.get(
            subcategory.name.strip().lower(),
            'fa-solid fa-layer-group'
        )

    return subcategories