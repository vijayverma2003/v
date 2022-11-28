from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse
from . import models
from .utils import calculate_total_cost, calculate_total_tax


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['user']
    list_display = ['name', 'price', 'unit', 'tax', 'stock_data']
    list_per_page = 10
    ordering = ['name', 'price', 'tax']
    search_fields = ['name__istartswith']

    def stock_data(self, product):
        url = (
            reverse('admin:invoicing_stock_changelist') +
            '?' +
            urlencode({'product_id': product.id})
        )
        return format_html('<a href="{}">Stock Data</a>', url)


@admin.register(models.Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['added_on', 'product', 'value']
    list_per_page = 10
    ordering = ['added_on']


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
              'terms', 'customer', 'transport']
    autocomplete_fields = ['customer', 'transport']
    inlines = [InvoiceProductInline]
    list_display = ['number', 'date', 'grand_total',
                    'customer_name', 'payments_data', 'transporter']
    list_select_related = ['customer']
    list_per_page = 10
    ordering = ['number']

    def grand_total(self, invoice):
        return self.total_cost(invoice) + self.total_tax(invoice)

    def customer_name(self, invoice):
        url = reverse('admin:invoicing_customer_changelist') + \
            '?' + urlencode({'id': invoice.customer.id})
        return format_html('<a href="{}"> {} </>', url, invoice.customer.name)

    def total_cost(self, invoice):
        total_cost = 0

        for item in list(invoice.invoiceitems.all()):
            total_cost += calculate_total_cost(item)

        return total_cost

    def total_tax(self, invoice):
        total_tax = 0

        for item in list(invoice.invoiceitems.all()):
            total_tax += calculate_total_tax(item)

        return total_tax

    def payments_data(self, invoice):
        url = (
            reverse('admin:invoicing_payment_changelist') +
            '?' +
            urlencode({'invoice_id': invoice.id})
        )

        return format_html('<a href="{}">Payments</a>', url)

    def transporter(self, invoice):
        url = (
            reverse('admin:invoicing_transport_changelist') +
            '?' +
            urlencode({'transport_id': invoice.transport.id})
        )

        return format_html('<a href="{}">{}</a>', url, invoice.transport.transporter_id)


@admin.register(models.Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'amount', 'datetime', 'mode']
    list_per_page = 10
    ordering = ['datetime']


@admin.register(models.Transport)
class TransportAdmin(admin.ModelAdmin):
    list_display = ['name', 'transporter_id', 'mode']
    list_per_page = 10
    ordering = ['mode']
    search_fields = ['name']
