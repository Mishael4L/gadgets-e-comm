from .models import Base, Category
from django.db.models import Count

def cart_count(request):
    if request.user.is_authenticated:
        count = sum(item.quantity for item in request.user.cart_items.all())
    else:
        cart = request.session.get('cart', {})
        count = sum(cart.values()) 
    return {'cart_count': count}

def base_info(request):
    base = Base.objects.first()
    category = Category.objects.annotate(product_count=Count('product'))
    return {'base': base,
            'category': category}
