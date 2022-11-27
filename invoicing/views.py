from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Product, Stock, Invoice, InvoiceItem, Transport
from .serializers import ProductSerializer, StockSerializer, InvoiceSerializer, TransportSerializer, AddInvoiceItemSerializer, InvoiceItemSerializer, CreateInvoiceSerializer
from .pagination import DefaultPagination

# Create your views here.


class ProductViewSet(ModelViewSet):
    filter_backends = [SearchFilter, OrderingFilter]
    ordering_fields = ['price', 'tax']
    queryset = Product.objects.all()
    search_fields = ['name']
    serializer_class = ProductSerializer
    pagination_class = DefaultPagination

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


class InvoiceViewSet(ModelViewSet):
    queryset = Invoice.objects.prefetch_related('invoiceitems__product').all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateInvoiceSerializer
        return InvoiceSerializer


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
