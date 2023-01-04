from invoicing.models import Invoice, Payment
from model_bakery import baker
from rest_framework import status
import pytest


@pytest.fixture
def create_payment(api_client):
    def do_create_payment(invoice_id, payment):
        return api_client.post(f'/invoicing/invoices/{invoice_id}/payments/', payment)
    return do_create_payment


@pytest.mark.django_db
class TestCreatePayment:
    def test_if_user_is_anonymous_returns_401(self, create_payment):
        invoice = baker.make(Invoice)

        response = create_payment(invoice.id, {'amount': 100, 'mode': 'cash'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_valid_returns_201(self, authenticate, create_payment):
        authenticate()
        invoice = baker.make(Invoice)

        response = create_payment(invoice.id, {'amount': 100, 'mode': 'cash'})

        assert response.status_code == status.HTTP_201_CREATED

    def test_if_data_is_invalid_returns_400(self, authenticate, create_payment):
        authenticate()
        invoice = baker.make(Invoice)

        response = create_payment(
            invoice.id, {'amount': '', 'mode': 'cash'})

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestRetrievePayment:
    def test_if_payment_exists_returns_200(self, api_client):
        payment = baker.make(Payment)

        response = api_client.get(
            f'/invoicing/invoices/{payment.invoice_id}/payments/{payment.id}/')

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestRetrievePaymentList:
    def test_if_payment_exists_returns_200(self, api_client):
        invoice = baker.make(Invoice)
        baker.make(Payment, invoice_id=invoice.id, _quantity=10)

        response = api_client.get(
            f'/invoicing/invoices/{invoice.id}/payments/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 10


@pytest.mark.django_db
class TestUpdatePayment:
    def test_if_data_is_valid_returns_200(self, authenticate, api_client):
        payment = baker.make(Payment)

        authenticate()

        response = api_client.put(f'/invoicing/invoices/{payment.invoice_id}/payments/{payment.id}/', {
            'amount': 10, 'mode': 'cash'})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['amount'] == 10
        assert response.data['mode'] == 'cash'

    def test_if_user_is_anonymous_returns_401(self, api_client):
        payment = baker.make(Payment)

        response = api_client.put(f'/invoicing/invoices/{payment.invoice_id}/payments/{payment.id}/', {
            'amount': 10, 'mode': 'cash'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_data_is_invalid_returns_400(self, authenticate, api_client):
        payment = baker.make(Payment)
        authenticate()

        response = api_client.put(f'/invoicing/invoices/{payment.invoice_id}/payments/{payment.id}/', {
            'amount': '', 'mode': 'cash'})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
