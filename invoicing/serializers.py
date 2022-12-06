from rest_framework import serializers
from .models import Product, Stock, Invoice, InvoiceItem, Transport, Payment, Customer, Address, Firm
from .utils import calculate_total_cost, calculate_total_tax


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['street', 'city', 'state', 'country']
        model = Address

    def create(self, validated_data):
        return Address.objects.create(firm_id=self.context.get('firm_id'), **validated_data)


class FirmSerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True)

    class Meta:
        fields = ['id', 'user', 'name', 'address']
        model = Firm


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['id', 'value', 'added_on']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return Stock.objects.create(product_id=product_id, **validated_data)


class ProductSerializer(serializers.ModelSerializer):
    stock = StockSerializer(many=True, read_only=True)
    user = serializers.IntegerField(read_only=True, source='user_id')
    # price_with_tax = serializers.SerializerMethodField(
    #     method_name='calculate_tax')

    class Meta:
        model = Product
        fields = ['id', 'user', 'name', 'price', 'tax', 'stock']

    def calculate_tax(self, product: Product):
        return product.price + product.price * (product.tax / 100)

    def create(self, validated_data):
        return Product.objects.create(user_id=self.context['user_id'], **validated_data)


class CustomerSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(read_only=True, source='user_id')

    class Meta:
        fields = ['id', 'user', 'name', 'phone', 'email',
                  'street', 'city', 'state', 'country']
        model = Customer

    def create(self, validated_data):
        return Customer.objects.create(user_id=self.context['user_id'], **validated_data)


class TransportSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'name', 'transporter_id', 'mode']
        model = Transport


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


class AddInvoiceItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                'No product with the given ID was found.')
        return value

    class Meta:
        model = InvoiceItem
        fields = ['id', 'product_id', 'price',
                  'discount', 'packing_charges', 'quantity']

    def create(self, validated_data):
        invoice_id = self.context.get('invoice_id')
        return InvoiceItem.objects.create(invoice_id=invoice_id, **validated_data)


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(
        many=True, source='invoiceitems', read_only=True)
    transport = TransportSerializer()

    total_cost = serializers.SerializerMethodField(
        method_name='calculate_total_cost')
    total_tax = serializers.SerializerMethodField(
        method_name='calculate_total_tax')
    customer = CustomerSerializer()
    firm = FirmSerializer()

    class Meta:
        model = Invoice
        fields = ['id', 'user', 'firm', 'number', 'date', 'due_date',
                  'customer', 'items', 'total_cost', 'total_tax', 'transport']

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


class CreateInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['id', 'number', 'date', 'due_date',
                  'customer', 'transport']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'amount', 'datetime', 'mode']
        model = Payment

    def create(self, validated_data):
        invoice_id = self.context['invoice_id']
        return Payment.objects.create(invoice_id=invoice_id, **validated_data)
