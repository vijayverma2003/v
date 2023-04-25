from .models import Product, Stock, Invoice, InvoiceItem, Transport, Payment, Customer, Address, Firm, FirmLogo, Bank
from .utils import calculate_total_cost, calculate_total_tax
from core.serializers import CountrySerializer
from django.db import transaction
from rest_framework import serializers


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['name', 'ifsc', 'acc', 'branch']
        model = Bank

    def create(self, validated_data):
        return Bank.objects.create(firm_id=self.context['firm_id'], **validated_data)


class AddressSerializer(serializers.ModelSerializer):
    country = CountrySerializer()

    class Meta:
        fields = ['street', 'city', 'state', 'country']
        model = Address


class CreateAddressSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ['street', 'city', 'state', 'country']
        model = Address

    def create(self, validated_data):
        return Address.objects.create(firm_id=self.context.get('firm_id'), **validated_data)


class FirmLogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FirmLogo
        fields = ['image']

    def create(self, validated_data):
        return FirmLogo.objects.create(firm_id=self.context['firm_id'], **validated_data)


class FirmSerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True)
    user_id = serializers.IntegerField(read_only=True)
    logo = FirmLogoSerializer(read_only=True)
    bank = BankSerializer(read_only=True)

    class Meta:
        fields = ['id', 'user_id', 'name', 'gstin', 'address', 'logo', 'bank']
        model = Firm

    def create(self, validated_data):
        return Firm.objects.create(user_id=self.context['user_id'], **validated_data)


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['id', 'value', 'added_on']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return Stock.objects.create(product_id=product_id, **validated_data)


class SimpleInvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ['invoice', 'quantity', 'price']


class ProductSerializer(serializers.ModelSerializer):
    stock = StockSerializer(many=True, read_only=True)
    user = serializers.IntegerField(read_only=True, source='user_id')
    invoice_items = SimpleInvoiceItemSerializer(
        many=True, read_only=True, source="product")

    class Meta:
        model = Product
        fields = ['id', 'user', 'name', 'price', 'tax',
                  'unit', 'hsn', 'stock', 'invoice_items']

    def calculate_tax(self, product: Product):
        return product.price + product.price * (product.tax / 100)

    def create(self, validated_data):
        return Product.objects.create(user_id=self.context['user_id'], **validated_data)


class SimpleInvoiceSerializer(serializers.ModelSerializer):
    total_cost = serializers.SerializerMethodField("calculate_total_cost")
    total_tax = serializers.SerializerMethodField("calculate_total_tax")

    class Meta:
        model = Invoice
        fields = ['id', 'number', 'date', 'total_cost', 'total_tax']

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


class CustomerSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(read_only=True, source='user_id')
    country = CountrySerializer()
    invoices = SimpleInvoiceSerializer(
        many=True, source='invoice_set', read_only=True)

    class Meta:
        fields = ['id', 'user', 'name', 'gstin', 'phone', 'email',
                  'street', 'city', 'state', 'country', 'invoices']
        model = Customer

    def create(self, validated_data):
        return Customer.objects.create(user_id=self.context['user_id'], **validated_data)


class CreateCustomerSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(read_only=True, source='user_id')

    class Meta:
        fields = ['id', 'user', 'name', 'gstin', 'phone', 'email',
                  'street', 'city', 'state', 'country']
        model = Customer

    def create(self, validated_data):
        return Customer.objects.create(user_id=self.context['user_id'], **validated_data)

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response = CustomerSerializer(instance).data
        return response


class TransportSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'name', 'transporter_id', 'mode', 'user_id']
        model = Transport

    def create(self, validated_data):
        return Transport.objects.create(user_id=self.context['user_id'], **validated_data)


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'tax', 'unit', 'hsn']


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

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                'No product with the given ID was found.')
        return value

    class Meta:
        model = InvoiceItem
        fields = ['id', 'product', 'price',
                  'discount', 'packing_charges', 'quantity']


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()


class SimpleCustomerSerializer(serializers.ModelSerializer):
    country = CountrySerializer()

    class Meta:
        fields = ['id', 'name', 'gstin', 'phone', 'email',
                  'street', 'city', 'state', 'country']
        model = Customer


class SimplePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'amount', 'datetime', 'mode']
        model = Payment


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(
        many=True, source='invoiceitems', read_only=True)
    transport = TransportSerializer()

    total_cost = serializers.SerializerMethodField(
        method_name='calculate_total_cost')
    total_tax = serializers.SerializerMethodField(
        method_name='calculate_total_tax')
    customer = SimpleCustomerSerializer()
    firm = FirmSerializer()
    user = UserSerializer()
    payments = SimplePaymentSerializer(source="payment_set", many=True)

    class Meta:
        model = Invoice
        fields = ['id', 'user', 'firm', 'number', 'date', 'due_date',
                  'customer', 'items', 'total_cost', 'total_tax', 'transport', 'payments']

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
    items = AddInvoiceItemSerializer(many=True, source="invoiceitems")

    class Meta:
        model = Invoice
        fields = ['id', 'firm', 'number', 'date', 'due_date',
                  'customer', 'transport', 'items']

    def create(self, validated_data):
        print(validated_data)
        items = validated_data.pop('invoiceitems')

        with transaction.atomic():
            invoice = Invoice.objects.create(
                user_id=self.context['user_id'], **validated_data)

            for item in items:
                InvoiceItem.objects.create(
                    invoice=invoice, price=item['price'], product=item['product'], quantity=item['quantity'])

            return invoice

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response = InvoiceSerializer(instance).data
        return response


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'amount', 'datetime', 'mode', 'invoice']
        model = Payment


class CreatePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'amount', 'datetime', 'mode']
        model = Payment

    def create(self, validated_data):
        invoice_id = self.context['invoice_id']
        return Payment.objects.create(invoice_id=invoice_id, **validated_data)

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response = PaymentSerializer(instance).data
        return response
