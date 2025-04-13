from django.contrib import admin

from ecom_app.models import Category, Customer, Order, Product,Cart

admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Cart)
