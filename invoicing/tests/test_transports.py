from django.contrib.auth import get_user_model
from invoicing.models import Transport
from model_bakery import baker
from rest_framework import status
import pytest


@pytest.fixture
def create_transport(api_client):
    def do_create_transport(transport):
        return api_client.post('/invoicing/transports/', transport)
    return do_create_transport


@pytest.mark.django_db
class TestCreateTransport:
    sample_transport = {'name': 'a', 'mode': 'a',
                        'transporter_id': 'a', 'user_id': 1}

    def test_if_user_is_anonymous_returns_401(self, create_transport):
        response = create_transport(self.sample_transport)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_valid_returns_201(self, authenticate, create_transport):
        user = get_user_model().objects.create()
        authenticate(id=user.id)

        response = create_transport(
            {**self.sample_transport, 'user_id': user.id})

        assert response.status_code == status.HTTP_201_CREATED

    def test_if_user_is_valid_but_data_is_invalid_returns_400(self, authenticate, create_transport):
        user = get_user_model().objects.create()
        authenticate(id=user.id)

        response = create_transport(
            {**self.sample_transport, 'name': '', 'user_id': user.id})

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestRetrieveTransport:
    def test_if_transport_exists_returns_200(self, api_client):
        user = get_user_model().objects.create()

        transport = baker.make(Transport, user_id=user.id)

        response = api_client.get(f'/invoicing/transports/{transport.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'id': transport.id,
            'name': transport.name,
            'transporter_id': transport.transporter_id,
            'mode': transport.mode,
            'user_id': transport.user_id
        }


@pytest.mark.django_db
class TestRetrieveTransports:
    def test_transports_list_endpoint_returns_200(self, api_client):
        user = get_user_model().objects.create()

        baker.make(Transport, user_id=user.id, _quantity=10)

        response = api_client.get(f'/invoicing/transports/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 10


@pytest.mark.django_db
class TestUpdateTransport:
    def test_if_user_is_anonymous_returns_401(self, create_transport):
        response = create_transport({'name': 'a', 'mode': 'a',
                                     'transporter_id': 'a', 'user_id': 1})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_valid_returns_404(self, authenticate, api_client):
        user = get_user_model().objects.create()

        authenticate(id=user.id)

        transport = baker.make(Transport, user_id=user.id, transporter_id="")

        response = api_client.put(
            f'/invoicing/transports/{transport.id}/', {**transport.__dict__, 'name': 'a'})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'a'
