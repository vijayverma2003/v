from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse
from . import models

# Register your models here.


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'unit', 'tax']
    list_per_page = 10
    ordering = ['name', 'price', 'tax']
    search_fields = ['name__istartswith']


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'address', 'invoice_count']
    list_filter = ['address__country']
    list_per_page = 10
    list_select_related = ['address']
    search_fields = ['name__istartswith']

    def invoice_count(self, customer):
        url = (
            reverse('admin:invoicing_invoice_changelist') +
            '?' +
            urlencode({
                'customer__id': str(customer.id)
            })
        )
        return format_html('<a href="{}"> {} </>', url, customer.invoice_count)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('invoice_set').annotate(invoice_count=Count('invoice'))


class InvoiceProductInline(admin.TabularInline):
    model = models.InvoiceItem
    autocomplete_fields = ['product']
    min_num = 1


@admin.register(models.Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    fields = ['number', 'date', 'due_date',
              'terms', 'customer', 'total', 'tax']
    autocomplete_fields = ['customer']
    inlines = [InvoiceProductInline]
    list_display = ['number', 'date', 'due_date',
                    'grand_total', 'customer_name']
    list_select_related = ['customer']
    list_per_page = 10
    ordering = ['number']

    def grand_total(self, invoice):
        return invoice.total + invoice.tax

    def customer_name(self, invoice):
        url = reverse('admin:invoicing_customer_changelist') + \
            '?' + urlencode({'id': invoice.customer.id})
        return format_html('<a href="{}"> {} </>', url, invoice.customer.name)
