from django.contrib.auth import get_user_model
from invoicing.models import Invoice, Customer, Firm, Product, InvoiceItem
from model_bakery import baker
from rest_framework import status
import pytest
import json


@pytest.fixture
def create_invoice(api_client):
    def do_create_invoice(invoice):
        data = json.dumps(invoice)
        return api_client.post('/invoicing/invoices/', data=data, content_type='application/json')
    return do_create_invoice


@pytest.mark.django_db
class TestCreateInvoice:

    def test_if_user_is_anoymous_returns_401(self, create_invoice):
        user = get_user_model().objects.create()
        customer = baker.make(Customer, user_id=user.id)
        firm = baker.make(Firm, user_id=user.id)
        product = baker.make(Product)

        response = create_invoice({'number': '1',
                                   'date': '2023-01-01',
                                   'due_date': '2023-01-01',
                                   'customer': customer.id,
                                   'firm': firm.id,
                                   'items': [
                                       {'product': product.id,
                                        'price': 100,
                                        'quantity': 1,
                                        'packing_charges': 0,
                                        'discount': 0
                                        }
                                   ]})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_valid_returns_201(self, authenticate, create_invoice):
        user = get_user_model().objects.create()
        customer = baker.make(Customer, user_id=user.id)
        firm = baker.make(Firm, user_id=user.id)
        product = baker.make(Product, user_id=user.id)

        authenticate(id=user.id)

        data = {'number': '1',
                'date': '2023-01-01',
                'due_date': '2023-01-01',
                'customer': customer.id,
                'firm': firm.id,
                'items': [
                    {'product': product.id,
                     'price': 100,
                     'quantity': 1,
                     'packing_charges': 0,
                     'discount': 0
                     }
                ]}

        response = create_invoice(data)

        print(response.data, response.status_code)

        assert response.status_code == status.HTTP_201_CREATED

    def test_if_data_is_invalid_returns_400(self, authenticate, create_invoice):
        user = get_user_model().objects.create()
        customer = baker.make(Customer, user_id=user.id)
        firm = baker.make(Firm, user_id=user.id)
        product = baker.make(Product)

        authenticate(id=user.id)

        response = create_invoice({'number': '1', 'date': '2023-01-01',
                                   'due_date': '2023-01-01', 'customer': customer.id, 'firm': firm.id,
                                   })

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestRetrieveInvoice:
    def test_if_invoice_exists_returns_200(self, api_client):
        invoice = baker.make(Invoice)

        response = api_client.get(f'/invoicing/invoices/{invoice.id}/')

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestRetrieveInvoiceList:
    def test_if_invoices_exists_returns_200(self, api_client):
        user = get_user_model().objects.create()
        baker.make(Invoice, user_id=user.id, _quantity=10)

        response = api_client.get(
            f'/invoicing/invoices/?user_id={user.id}')
        print(len(response.data))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 10


@pytest.mark.django_db
class TestUpdateInvoice:
    def test_if_user_is_anoymous_returns_401(self, api_client):
        user = get_user_model().objects.create()
        customer = baker.make(Customer, user_id=user.id)
        firm = baker.make(Firm, user_id=user.id)
        invoice = baker.make(Invoice, customer_id=customer.id,
                             firm_id=firm.id, user_id=user.id)
        invoice_item = baker.make(InvoiceItem, invoice_id=invoice.id)

        response = api_client.put(f'/invoicing/invoices/{invoice.id}/', {'number': '1', 'date': '2023-01-01',
                                                                         'due_date': '2023-01-01', 'customer': customer.id, 'firm': firm.id,
                                                                         'items': [{'product': invoice_item.product.id, 'price': 100, 'quantity': 1, 'packing_charges': 0, 'discount': 0}]})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_authenticated_and_data_is_valid_returns_200(self, authenticate, api_client):
        user = get_user_model().objects.create()
        customer = baker.make(Customer, user_id=user.id)
        firm = baker.make(Firm, user_id=user.id)
        invoice = baker.make(Invoice, customer_id=customer.id,
                             firm_id=firm.id, user_id=user.id)
        invoice_item = baker.make(InvoiceItem, invoice_id=invoice.id)

        authenticate(id=user.id)

        response = api_client.put(f'/invoicing/invoices/{invoice.id}/',
                                  json.dumps({'number': '1', 'date': '2023-01-01',
                                              'due_date': '2023-01-01', 'customer': customer.id, 'firm': firm.id,
                                              'items': [{'product': invoice_item.product.id, 'price': 100, 'quantity': 1, 'packing_charges': 0, 'discount': 0}]}),
                                  content_type="application/json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data['number'] == '1'

    def test_if_user_is_authenticated_and_data_is_invalid_returns_200(self, authenticate, api_client):
        user = get_user_model().objects.create()
        customer = baker.make(Customer, user_id=user.id)
        firm = baker.make(Firm, user_id=user.id)
        invoice = baker.make(Invoice, customer_id=customer.id,
                             firm_id=firm.id, user_id=user.id)

        authenticate(id=user.id)

        response = api_client.put(f'/invoicing/invoices/{invoice.id}/', {'number': '', 'date': '2023-01-01',
                                                                         'due_date': '2023-01-01', 'customer': customer.id, 'user': user.id, 'firm': firm.id})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
