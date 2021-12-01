from django.contrib import admin
from pos_app.models import Product, OrderProduct, Order, Category
# Register your models here.
admin.site.register(Product)
admin.site.register(OrderProduct)
admin.site.register(Order)
admin.site.register(Category)
