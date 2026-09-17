from django.urls import path
from . import views
from django.conf.urls.static import static

urlpatterns = [
    path('', views.landing_pg, name='landing'),
    path('shop/', views.shop_pg, name='shop'),
    path('product/<slug:slug>/', views.product_pg, name='product'),
    path('cart/', views.cart_pg, name='cart'),
    path('cart/add/<slug:slug>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<slug:slug>/', views.update_cart, name='update_cart'),
    path('cart/remove/<slug:slug>/', views.remove_from_cart, name='remove_from_cart'),
    path('contact/', views.contact_pg, name='contact'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('orders/', views.order_history, name='order_history'),
    path('newsletter-signup/', views.newsletter_signup, name='newsletter_signup'),
]
