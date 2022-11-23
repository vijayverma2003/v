from django.contrib import admin
from . import models

# Register your models here.


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'unit', 'tax']
    list_per_page = 10
    ordering = ['name', 'price', 'tax']


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email']
    list_per_page = 10
