from django.contrib.auth import get_user_model
from invoicing.models import Firm
from model_bakery import baker
from rest_framework import status
import pytest


@pytest.fixture
def create_firm(api_client):
    def do_create_firm(firm):
        return api_client.post('/invoicing/firms/', firm)
    return do_create_firm


@pytest.mark.django_db
class TestCreateFirm:
    def test_if_user_is_anonymous_returns_401(self, create_firm):
        response = create_firm({'name': 'a'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_valid_returns_201(self, create_firm, authenticate):
        user = get_user_model().objects.create()
        print(user)
        authenticate(id=user.id)

        response = create_firm({'name': 'a'})

        assert response.status_code == status.HTTP_201_CREATED

    def test_if_data_is_invalid_returns_400(self, create_firm, authenticate):
        user = get_user_model().objects.create()
        authenticate(id=user.id)

        response = create_firm({'name': ''})

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestRetrieveFirm:
    def test_if_firm_exists_returns_200(self, api_client):
        user = get_user_model().objects.create()

        firm = baker.make(Firm, user_id=user.id)

        response = api_client.get(f'/invoicing/firms/{firm.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'id': firm.id,
            'name': firm.name,
            'gstin': firm.gstin,
            'user_id': user.id,
            'address': None,
            'logo': None,
        }


@pytest.mark.django_db
class TestRetrieveFirmList:
    def test_if_firm_exists_returns_200(self, api_client):
        baker.make(Firm, _quantity=10)

        response = api_client.get(f'/invoicing/firms/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 10


@pytest.mark.django_db
class TestUpdateFirm:
    def test_if_user_is_valid_returns_200(self, authenticate, api_client):
        firm = baker.make(Firm)

        authenticate(id=firm.user_id)

        response = api_client.put(
            f'/invoicing/firms/{firm.id}/', {**firm.__dict__, 'name': 'a', 'gstin': ''})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'a'
