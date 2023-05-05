from django.contrib.auth import get_user_model
from invoicing.models import Customer
from model_bakery import baker
from rest_framework import status
from core.models import Country
import pytest


@pytest.fixture
def create_customer(api_client):
    def do_create_customer(customer):
        return api_client.post('/invoicing/customers/', customer)
    return do_create_customer


@pytest.mark.django_db
class TestCreateCustomer:
    sample_customer = {'name': 'a', 'phone': 'a',
                                    'email': 'a@domain.com', 'city': 'a', 'state': 'a', 'country': 'a', 'user_id': 1}

    def test_if_user_is_anonymous_returns_401(self, create_customer):
        response = create_customer(self.sample_customer)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_anonymous_returns_201(self, authenticate, create_customer):
        user = get_user_model().objects.create()
        country = baker.make(Country)
        authenticate(id=user.id)

        response = create_customer(
            {**self.sample_customer, 'country': country.id})

        print(response.data)

        assert response.status_code == status.HTTP_201_CREATED

    def test_if_data_is_invalid_returns_400(self, authenticate, create_customer):
        user = get_user_model().objects.create()
        authenticate(id=user.id)

        response = create_customer(
            {**self.sample_customer, 'name': ''})

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestRetrieveCustomer:
    def test_if_customer_exists_returns_200(self, api_client):
        user = get_user_model().objects.create()
        customer = baker.make(Customer, user_id=user.id)

        response = api_client.get(f'/invoicing/customers/{customer.id}/')

        print(response.data.__dict__)
        print(customer.country.__dict__)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'city': customer.city,
            'country': customer.country,
            'email': customer.email,
            'gstin': customer.gstin,
            'id': customer.id,
            'name': customer.name,
            'phone': customer.phone,
            'state': customer.state,
            'street': customer.street,
            'user': user.id,
            'country': {'id': customer.country.id, 'idd': customer.country.idd, 'name': customer.country.name,
                        'currency':
                        {
                            'id': customer.country.currency.id,
                            'label': customer.country.currency.label,
                            'name': customer.country.currency.name,
                            'smaller_unit': customer.country.currency.smaller_unit,
                            'symbol': customer.country.currency.symbol,
                        }},
            'invoices': []
        }


@pytest.mark.django_db
class TestRetrieveCustomers:
    def test_if_customers_list_endpoint_returns_200(self, api_client):
        baker.make(Customer, _quantity=10)

        response = api_client.get(f'/invoicing/customers/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 10


@pytest.mark.django_db
class TestUpdateCustomer:
    def test_if_user_is_valid_returns_404(self, authenticate, api_client):
        user = get_user_model().objects.create()
        authenticate(id=user.id)
        customer = baker.make(Customer, user_id=user.id)

        response = api_client.put(
            f'/invoicing/customers/{customer.id}/', {**customer.__dict__, 'name': 'a', 'gstin': '', 'street': '', 'country': customer.country.id})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'a'
