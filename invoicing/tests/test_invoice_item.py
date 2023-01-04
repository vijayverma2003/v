from invoicing.models import Invoice, Product, InvoiceItem
from model_bakery import baker
from rest_framework import status
import pytest


@pytest.fixture
def create_invoice_item(api_client):
    def do_create_invoice_item(invoice_id, item):
        return api_client.post(f'/invoicing/invoices/{invoice_id}/items/', item)
    return do_create_invoice_item


@pytest.mark.django_db
class TestCreateInvoiceItem:
    def test_if_user_is_anonymous_returns_401(self,  create_invoice_item):
        invoice = baker.make(Invoice)
        product = baker.make(Product)

        response = create_invoice_item(
            invoice.id, {'product': product.id, 'price': 1, 'quantity': 1})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_data_is_valid_returns_201(self, authenticate, create_invoice_item):
        invoice = baker.make(Invoice)
        product = baker.make(Product)

        authenticate()

        response = create_invoice_item(
            invoice.id, {'product': product.id, 'price': 1, 'quantity': 1})

        assert response.status_code == status.HTTP_201_CREATED

    def test_if_data_is_invalid_returns_400(self, authenticate, create_invoice_item):
        invoice = baker.make(Invoice)
        product = baker.make(Product)

        authenticate()

        response = create_invoice_item(
            invoice.id, {'product': product.id, 'price': '', 'quantity': 1})

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestRetrieveInvoiceItem:
    def test_if_invoice_item_exists_returns_200(self, api_client):
        invoice = baker.make(Invoice)
        invoice_item = baker.make(InvoiceItem, invoice_id=invoice.id)

        response = api_client.get(
            f'/invoicing/invoices/{invoice.id}/items/{invoice_item.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == invoice_item.id
        assert response.data['quantity'] == invoice_item.quantity


@pytest.mark.django_db
class TestRetrieveInvoiceItemList:
    def test_if_invoice_items_exists_returns_200(self, api_client):
        invoice = baker.make(Invoice)
        baker.make(
            InvoiceItem, invoice_id=invoice.id, _quantity=10)

        response = api_client.get(
            f'/invoicing/invoices/{invoice.id}/items/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 10


@pytest.mark.django_db
class UpdateRetrieveInvoiceItemList:
    def test_if_user_is_anonymous_returns_401(self,  api_client):
        invoice_item = baker.make(InvoiceItem)

        response = api_client.put(f'/invoicing/invoices/{invoice_item.invoice.id}/items/{invoice_item.id}/',
                                  {'invoice_id': invoice_item.invoice.id, 'product': invoice_item.product.id, 'price': 1, 'quantity': 1})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_data_is_valid_returns_200(self, authenticate, api_client):
        invoice_item = baker.make(InvoiceItem)
        authenticate()

        response = api_client.put(f'/invoicing/invoices/{invoice_item.invoice.id}/items/{invoice_item.id}/',
                                  {'invoice_id': invoice_item.invoice.id, 'product': invoice_item.product.id, 'price': 10, 'quantity': 1})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['price'] == 10

    def test_if_data_is_invalid_returns_400(self, authenticate, api_client):
        invoice_item = baker.make(InvoiceItem)
        authenticate()

        response = api_client.put(f'/invoicing/invoices/{invoice_item.invoice.id}/items/{invoice_item.id}/',
                                  {'invoice_id': invoice_item.invoice.id, 'product': invoice_item.product.id, 'price': '', 'quantity': 1})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
