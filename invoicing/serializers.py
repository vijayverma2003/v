from rest_framework import serializers
from .models import Product, Stock, Invoice, InvoiceItem
from decimal import Decimal


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['id', 'value', 'added_on']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return Stock.objects.create(product_id=product_id, **validated_data)


class ProductSerializer(serializers.ModelSerializer):
    # price_with_tax = serializers.SerializerMethodField(
    #     method_name='calculate_tax')
    stock = StockSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'tax', 'stock']

    def calculate_tax(self, product: Product):
        return product.price + product.price * (product.tax / 100)


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'tax', 'unit']


def calculate_total_cost(item):
    total = (item.price + item.packing_charges) * \
        item.quantity
    return total - round(Decimal(item.discount / 100), 2) * total


class InvoiceItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total = serializers.SerializerMethodField(method_name='calculate_total')

    class Meta:
        model = InvoiceItem
        fields = ['id', 'product', 'price',
                  'discount', 'packing_charges', 'quantity', 'total']

    def calculate_total(self, invoiceitem):
        return calculate_total_cost(invoiceitem)


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, source='invoiceitems')
    total_price = serializers.SerializerMethodField(
        method_name='calculate_total_price')

    class Meta:
        model = Invoice
        fields = ['id', 'number', 'date', 'due_date',
                  'customer', 'total', 'tax', 'customer', 'items', 'total_price']

    def calculate_total_price(self, invoice):
        total_price = 0

        for item in list(invoice.invoiceitems.all()):
            total_price += calculate_total_cost(item)

        return total_price
