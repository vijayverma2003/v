from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, AllowAny

# from .pagination import DefaultPagination
from .models import Product, Stock, Invoice, InvoiceItem, Transport, Payment, Customer, Firm, Address
from .serializers import AddInvoiceItemSerializer,\
    AddressSerializer,\
    CreateInvoiceSerializer,\
    CustomerSerializer,\
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
            return Product.objects.filter(user_id=self.request.user.id)
        return Product.objects.all()

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
    queryset = Invoice.objects.prefetch_related('invoiceitems__product').all()

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT']:
            return CreateInvoiceSerializer
        return InvoiceSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]


class TransportViewSet(ModelViewSet):
    queryset = Transport.objects.all()
    serializer_class = TransportSerializer


class InvoiceItemViewSet(ModelViewSet):

    def get_queryset(self):
        return InvoiceItem.objects.filter(invoice_id=self.kwargs['invoice_pk']).select_related('product')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddInvoiceItemSerializer
        return InvoiceItemSerializer

    def get_serializer_context(self):
        return {'invoice_id': self.kwargs['invoice_pk']}


class PaymentViewSet(ModelViewSet):
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(invoice_id=self.kwargs['invoice_pk'])

    def get_serializer_context(self):
        return {'invoice_id': self.kwargs['invoice_pk']}


class FirmViewSet(ModelViewSet):
    serializer_class = FirmSerializer

    def get_queryset(self):
        return Firm.objects.select_related('address').all()


class AddressViewSet(ModelViewSet):
    serializer_class = AddressSerializer

    def get_queryset(self):
        return Address.objects.filter(pk=self.kwargs['firm_pk'])

    def get_serializer_context(self):
        return {'firm_id': self.kwargs['firm_pk']}
