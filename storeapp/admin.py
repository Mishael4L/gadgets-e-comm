from django.contrib import admin
from .models import Base, Category, Product, Messageform, Contact, FAQ, Brand

# Register your models here.
admin.site.register(Base)
# admin.site.register(Shop)
# admin.site.register(Bycategory)
# admin.site.register(Foryou)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Contact)
admin.site.register(FAQ)
admin.site.register(Messageform)
admin.site.register(Brand)