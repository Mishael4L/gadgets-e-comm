from django.shortcuts import render, redirect
from django.contrib.auth import login, logout,authenticate, get_user_model
from django.contrib import messages
from .forms import RegisterForm, LoginForm
from storeapp.models import Product, CartItem

User = get_user_model()

# Create your views here.
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                email = form.cleaned_data['email'],
                password = form.cleaned_data['password'],
                first_name = form.cleaned_data['first_name'],
                last_name = form.cleaned_data['last_name'],
            )
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name}!')
            return redirect('landing')
    else:
        form = RegisterForm()

    context = {'form': form}
    return render(request, 'auth/register.html', context)


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                merge_session_cart(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('landing')
            else:
                messages.error(request, 'Invalid email or password')

    else:
        form = LoginForm()

    context = {'form' : form}
    return render(request, 'auth/login.html', context)


def merge_session_cart(request, user):
    session_cart = request.session.get('cart', {})
    if not session_cart:
        return

    for product_id, quantity in session_cart.items():
        product = Product.objects.filter(id=product_id).first()
        if not product:
            continue
        cart_item, created = CartItem.objects.get_or_create(user=user, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

    del request.session['cart']

def logout_view(request):
    logout(request)
    messages.success(request, "You've been logged out")
    return redirect('landing')


