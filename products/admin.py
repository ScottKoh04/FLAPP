from django.contrib import admin

# Register your models here.
from .models import User, Tier, Customer, Product, Order, Invoice

admin.site.register(User)
admin.site.register(Tier)
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Invoice)
