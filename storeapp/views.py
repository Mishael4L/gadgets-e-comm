from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.db.models import Count
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import logging

from .models import Product, Messageform, Contact, FAQ, Category, Brand, CartItem, Order, OrderItem 
from .forms import ContactForm, NewsletterForm

logger = logging.getLogger(__name__)

# Create your views here.
def landing_pg(request):
    product = Product.objects.all()[:5]
    foryou = Product.objects.filter(is_featured=True)[:4]
    category = Category.objects.annotate(product_count=Count('product'))
    context = {
        'product' : product, 

        'foryou' : foryou,

        'category': category,
    }

    return render(request, 'web/index.html', context)


def shop_pg(request):
    category = Category.objects.annotate(product_count=Count('product'))
    brand = Brand.objects.annotate(product_count=Count('product'))

    selected_category_slugs = request.GET.getlist('category') 
    selected_brand_slugs = request.GET.getlist('brand')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    search_query = request.GET.get('q')

    product = Product.objects.all().order_by('id')

    if search_query:
        product = product.filter(
            Q(name__icontains=search_query) |
            # Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(brand__name__icontains=search_query)
            )

    if selected_category_slugs:
        product = product.filter(category__slug__in=selected_category_slugs)

    if selected_brand_slugs:
        product = product.filter(brand__slug__in=selected_brand_slugs)

    if min_price:
        product = product.filter(price_now__gte=min_price)

    if max_price:
        product = product.filter(price_now__lte=max_price)

    total_count = product.count()
    paginator = Paginator(product, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category' : category,
        'brand' : brand,
        'page_obj' : page_obj,
        'product' : product,
        'total_count' : total_count,
        'selected_category_slugs' : selected_category_slugs,
        'selected_brand_slugs' : selected_brand_slugs,
        'min_price' : min_price,
        'max_price' : max_price,
        'search_query' : search_query,
    }

    return render(request, 'web/shop.html', context)


def product_pg(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.filter(category=product.category).exclude(slug=slug)[:4]
    context = {
        'product' : product,
        'related_products' : related_products,
    }

    return render(request, 'web/product.html', context)


def contact_pg(request):
    contact = Contact.objects.first()
    faq = FAQ.objects.all()

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()

            try:
                send_mail(
                    subject=f'{contact.get_subject_display()} — {contact.first_name} {contact.last_name}',
                    message=(
                        f'From: {contact.first_name} {contact.last_name} ({contact.email})\n'
                        f'Phone: {contact.phone or "Not provided"}\n'
                        f'Order number: {contact.order_number or "N/A"}\n\n'
                        f'Message:\n{contact.message}'
                    ),
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[settings.EMAIL_HOST_USER],
                    fail_silently=False,
                )
                messages.success(request, "Thank you for contacting us. We'll get back to you")

            except Exception as e:
                messages.warning(request, "Sorry, an error occured. kindly repeat the process")
                print(f"Email error: {e}")

            return redirect('contact')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = ContactForm()

    context = {'email' : contact.email,
               'phone' : contact.phone,
               'live_chat' : contact.live_chat,
               'address' : contact.address,

               'faq' : faq,

               'form' : form,
    }

    return render(request, 'web/contact.html', context)

def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)

    if request.user.is_authenticated:
        cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
    else:
        cart = request.session.get('cart', {})
        product_id = str(product.id)
        cart[product_id] = cart.get(product_id, 0) + 1
        request.session['cart'] = cart

    messages.success(request, f'{product.name} added to cart')
    return redirect('shop')

def update_cart(request, slug):
    if request.method == 'POST':
        product = get_object_or_404(Product, slug=slug)
        quantity = int(request.POST.get('quantity', 1))

        if request.user.is_authenticated:
            if quantity > 0:
                CartItem.objects.update_or_create(user=request.user, product=product, defaults={'quantity': quantity}
                )
            else:
                CartItem.objects.filter(user=request.user, product=product).delete()
    else:
        cart = request.session.get('cart', {})
        if quantity > 0:
            cart[str(product.id)] = quantity
        else:
            cart.pop(str(product.id), None)
        request.session['cart'] = cart

    return redirect('cart')

def remove_from_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)

    if request.user.is_authenticated:
        CartItem.objects.filter(user=request.user, product=product).delete()
    else:
        cart = request.session.get('cart', {})
        cart.pop(str(product.id), None)
        request.session['cart'] = cart

    messages.success(request, f'{product.name} removed from cart')
    return redirect('cart')

def cart_pg(request):
    cart_items = []
    grand_total = 0

    if request.user.is_authenticated:
        items = CartItem.objects.filter(user=request.user).select_related('product')

        for item in items:
            grand_total += item.subtotal
            cart_items.append({
                'product' : item.product,
                'quantity' : item.quantity,
                'subtotal' : item.subtotal,
            })
    else:
        cart = request.session.get('cart', {})
        for product_id, quantity in cart.items():
            product = get_object_or_404(Product, id=product_id)
            subtotal = product.price_now * quantity
            grand_total += subtotal
            cart_items.append({
                'product' : product,
                'quantity' : quantity,
                'subtotal' : subtotal,
            })
    
    context = {
        'cart_items' : cart_items,
        'grand_total' : grand_total,
    }

    return render(request, 'web/cart.html', context)

@login_required
def checkout_view(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')

    if not cart_items:
        messages.error(request, "Your cart is empty")
        return redirect('cart')

    grand_total = sum(item.subtotal for item in cart_items)

    order = Order.objects.create(user=request.user, total=grand_total)

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price_at_purchase=item.product.price_now
        )

    cart_items.delete()

    messages.success(request, f'Order #{order.id} placed successfully')
    return redirect('order_history')

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product').order_by('-created_at')
    context= {'orders': orders}
    return render(request, 'web/order_history.html', context)


def newsletter_signup(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "You're subscribed! Check your email for your 20% off code.")
        else:
            if 'email' in form.errors:
                messages.error(request, "That email is either invalid or you already subscribed")
    return redirect('landing')