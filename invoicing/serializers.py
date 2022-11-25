from rest_framework import serializers
from .models import Product, Stock, Invoice, InvoiceItem
from .utils import calculate_total_cost, calculate_total_tax


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
    total_cost = serializers.SerializerMethodField(
        method_name='calculate_total_cost')
    total_tax = serializers.SerializerMethodField(
        method_name='calculate_total_tax')

    class Meta:
        model = Invoice
        fields = ['id', 'number', 'date', 'due_date',
                  'customer', 'customer', 'items', 'total_cost', 'total_tax']

    def calculate_total_cost(self, invoice):
        total_cost = 0

        for item in list(invoice.invoiceitems.all()):
            total_cost += calculate_total_cost(item)

        return total_cost

    def calculate_total_tax(self, invoice):
        total_tax = 0

        for item in list(invoice.invoiceitems.all()):
            total_tax += calculate_total_tax(item)

        return total_tax
