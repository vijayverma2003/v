from .models import Product, Stock, Invoice, InvoiceItem, Transport, Payment, Customer, Firm, Address, FirmLogo
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from io import BytesIO
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from xhtml2pdf import pisa
from .serializers import AddInvoiceItemSerializer,\
    AddressSerializer,\
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
            return Invoice.objects.prefetch_related('invoiceitems__product')\
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


def render_to_pdf(request, id):
    if request.method == 'GET':
        invoice = {}

        try:
            invoice_data = Invoice.objects.prefetch_related(
                'customer', 'firm', 'user').get(id=id)
            invoice = InvoiceSerializer(invoice_data).data

        except Invoice.DoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

        # get_template looks for the template_path in the templates folder in current module.
        template_path = 'invoice_1.html'
        template = get_template(template_path)

        # render method of template takes a dictionary that can change data in HTML.
        html = template.render(invoice)

        result = BytesIO()

        # the pisaDocument method of pisa from xhtml2pdf takes a html file in decoded form of bytes.
        # Encode the html document first, and then pass it in the BytesIO
        pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)

        # Error while creating pdf returns 501 - Internal Server Error
        if not pdf.error:
            return HttpResponse({'error': "PDF can't be created."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        #  else returns the result that is returned by getvalue method of variable result
        #  with the content_type of 'application/pdf'
        response = HttpResponse(
            result.getvalue(), content_type='application/pdf')

        # response['Content-Disposition'] = f'attachment; filename="INV-{invoice["number"]}.pdf"'

        return response

        # If the method is not 'GET' then error 405 - Method not allowed is thrown
    else:
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)
