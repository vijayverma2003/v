from django.contrib.auth import get_user_model
from invoicing.models import Firm, Address
from model_bakery import baker
from rest_framework import status
from core.models import Country
import pytest


@pytest.fixture
def create_firm_address(api_client):
    def do_create_firm_address(firm_id, firm_address):
        return api_client.post(f'/invoicing/firms/{firm_id}/address/', firm_address)
    return do_create_firm_address


@pytest.mark.django_db
class TestCreateAddress:
    sample_address = {'state': 'a', 'city': 'a'}

    def test_if_user_is_anonymous_returns_401(self, create_firm_address):
        firm = baker.make(Firm)

        response = create_firm_address(
            firm.id, self.sample_address)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_valid_returns_201(self, authenticate,  create_firm_address):
        firm = baker.make(Firm)
        country = baker.make(Country)
        authenticate(firm.user_id)

        response = create_firm_address(
            firm.id, {**self.sample_address, 'country': country.id})

        assert response.status_code == status.HTTP_201_CREATED

    def test_if_data_is_invalid_returns_400(self, authenticate, create_firm_address):
        firm = baker.make(Firm)
        authenticate(firm.user_id)

        response = create_firm_address(
            firm.id, {**self.sample_address, 'state': ''})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_address_for_firm_already_exists(self, authenticate, create_firm_address):
        address = baker.make(Address)
        authenticate(address.firm.user_id)

        response = create_firm_address(
            address.firm.id, self.sample_address)

        print(response.status_code)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
class TestRetrieveFirmAddress:
    def test_if_address_exists_returns_200(self, api_client):
        address = baker.make(Address)

        response = api_client.get(
            f'/invoicing/firms/{address.firm.id}/address/{address.firm.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'street': address.street,
            'city': address.city,
            'state': address.state,
            'country': {'id': address.country.id, 'idd': address.country.idd, 'name': address.country.name,
                        'currency':
                        {
                            'id': address.country.currency.id,
                            'label': address.country.currency.label,
                            'name': address.country.currency.name,
                            'smaller_unit': address.country.currency.smaller_unit,
                            'symbol': address.country.currency.symbol,
                        }},
        }


@pytest.mark.django_db
class TestUpdateFirmAddress:
    def test_if_user_is_valid_returns_200(self, api_client, authenticate):
        address = baker.make(Address)
        authenticate(address.firm.user_id)

        response = api_client.put(
            f'/invoicing/firms/{address.firm.id}/address/{address.firm.id}/', {'state': 'a', 'city': 'a', 'country': address.country.id})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['state'] == 'a'
