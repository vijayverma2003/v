from .models import Product, Stock, Invoice, InvoiceItem, Transport, Payment, Customer, Firm, Address, FirmLogo, Bank
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from io import BytesIO
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from weasyprint import HTML
import base64
import chardet
import qrcode
from .serializers import AddInvoiceItemSerializer,\
    AddressSerializer,\
    BankSerializer,\
    CreateCustomerSerializer,\
    CreateInvoiceSerializer,\
    CustomerSerializer,\
    FirmLogoSerializer,\
    FirmSerializer,\
    InvoiceItemSerializer,\
    InvoiceSerializer,\
    PaymentSerializer,\
    ProductSerializer,\
    StockSerializer,\
    TransportSerializer\



def create_invoice_pdf(request, id):
    invoice = get_object_or_404(Invoice, pk=id)
    serializer = InvoiceSerializer(invoice)
    data = serializer.data

    taxList = []

    for item in data.get('items'):
        product = item.get('product')
        tax = product.get('tax')

        exists = False

        for rate in taxList:
            if rate.get('tax') and rate.get('tax') == tax:
                rate.total += item.get('total') * (tax / 100)
                exists = True

        if not exists:
            taxList.append(
                {'tax': tax, 'total': item.get('total') * (tax / 100)})

    qr = qrcode.QRCode(version=1, box_size=10, border=4,
                       error_correction=qrcode.constants.ERROR_CORRECT_L,)

    qr.add_data('https://google.com')
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()

    img.save(buffer, format="PNG")

    buffer_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

    html_template = get_template("invoice_1.html")

    html = html_template.render(
        {'inv': data, 'qr': f'data:image/png;base64,{buffer_image}', 'taxList': taxList, 'grand_total': data.get('total_cost') + data.get('total_tax')})

    html_bytes = html.encode()

    result = chardet.detect(html_bytes)

    rendered_html = html_bytes.decode(result['encoding']).encode("utf-8")

    pdf = HTML(string=rendered_html).write_pdf()

    return HttpResponse(pdf, content_type="application/pdf")


class ProductViewSet(ModelViewSet):
    filter_backends = [SearchFilter, OrderingFilter]
    ordering_fields = ['price', 'tax']
    search_fields = ['name']
    serializer_class = ProductSerializer

    def get_queryset(self):
        if self.request.user.id:
            return Product.objects.prefetch_related('stock').filter(user_id=self.request.user.id)
        return Product.objects.prefetch_related('stock').all()

    def get_serializer_context(self):
        return {'user_id': self.request.user.id}

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def destroy(self, request, *args, **kwargs):
        if InvoiceItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error': 'Product can not be deleted because it is associated with an invoice item.'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

        return super().destroy(request, *args, **kwargs)


class StockViewSet(ModelViewSet):
    serializer_class = StockSerializer

    def get_queryset(self):
        return Stock.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]


class CustomerViewSet(ModelViewSet):
    serializer_class = CustomerSerializer

    def get_queryset(self):
        if self.request.user.id:
            return Customer.objects.filter(user_id=self.request.user.id)
        return Customer.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT']:
            return CreateCustomerSerializer
        return CustomerSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_context(self):
        return {'user_id': self.request.user.id}

    def destroy(self, request, *args, **kwargs):
        if Invoice.objects.filter(customer_id=kwargs['pk']).count() > 0:
            return Response({'error': 'Customer can not be deleted because it is associated with an invoice.'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

        return super().destroy(request, *args, **kwargs)


class InvoiceViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_queryset(self):
        if self.request.user.id:
            return Invoice.objects.prefetch_related('invoiceitems__product') \
                .filter(user_id=self.request.user.id)
        return Invoice.objects.prefetch_related('invoiceitems__product').all()

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT']:
            return CreateInvoiceSerializer
        return InvoiceSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_context(self):
        return {'user_id': self.request.user.id}


class TransportViewSet(ModelViewSet):
    queryset = Transport.objects.all()
    serializer_class = TransportSerializer

    def get_queryset(self):
        if self.request.user.id:
            return Transport.objects.filter(user_id=self.request.user.id)
        return Transport.objects.all()

    def get_serializer_context(self):
        return {'user_id': self.request.user.id}

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]


class InvoiceItemViewSet(ModelViewSet):

    def get_queryset(self):
        return InvoiceItem.objects.filter(invoice_id=self.kwargs['invoice_pk']).select_related('product')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddInvoiceItemSerializer
        return InvoiceItemSerializer

    def get_serializer_context(self):
        return {'invoice_id': self.kwargs['invoice_pk']}

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]


class PaymentViewSet(ModelViewSet):
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(invoice_id=self.kwargs['invoice_pk'])

    def get_serializer_context(self):
        return {'invoice_id': self.kwargs['invoice_pk']}

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]


class FirmViewSet(ModelViewSet):
    serializer_class = FirmSerializer

    def get_queryset(self):
        if self.request.user.id:
            return Firm.objects.select_related('address', 'logo').filter(user_id=self.request.user.id)
        return Firm.objects.select_related('address', 'logo').all()

    def get_serializer_context(self):
        return {'user_id': self.request.user.id}

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        if Firm.objects.filter(user_id=self.request.user.id).exists():
            return Response({'error': 'Firm for the requested user already exists.'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().create(request, *args, **kwargs)


class AddressViewSet(ModelViewSet):
    serializer_class = AddressSerializer

    def get_queryset(self):
        return Address.objects.filter(pk=self.kwargs['firm_pk'])

    def get_serializer_context(self):
        return {'firm_id': self.kwargs['firm_pk']}

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        if Address.objects.filter(pk=kwargs['firm_pk']).exists():
            return Response({'error': 'Address already exists for the firm.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().create(request, *args, **kwargs)


class FirmLogoViewSet(ModelViewSet):
    serializer_class = FirmLogoSerializer

    def get_queryset(self):
        return FirmLogo.objects.filter(firm_id=self.kwargs['firm_pk'])

    def get_serializer_context(self):
        return {'firm_id': self.kwargs['firm_pk']}


class BankViewSet(ModelViewSet):
    serializer_class = BankSerializer

    def get_queryset(self):
        if self.request.user.id:
            return Bank.objects.filter(firm_id=self.kwargs['firm_pk'])
        return Bank.objects.all()

    def get_serializer_context(self):
        return {'firm_id': self.kwargs['firm_pk']}

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
