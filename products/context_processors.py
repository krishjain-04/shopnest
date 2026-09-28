from .models import Wishlist  # Adjust model import to your existing Wishlist model

def wishlist_processor(request):
    if request.user.is_authenticated:
        count = Wishlist.objects.filter(user=request.user).count()
    else:
        count = 0
    return {'wishlist_count': count}