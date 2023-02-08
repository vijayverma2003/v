from django.contrib.auth import get_user_model
from invoicing.models import Product
from model_bakery import baker
from rest_framework import status
import pytest


@pytest.fixture
def create_product(api_client):
    def do_create_product(product):
        return api_client.post('/invoicing/products/', product)
    return do_create_product


@pytest.mark.django_db
class TestCreateProduct:
    sample_product = {'name': 'a', 'price': 10,
                      'tax': 10, 'unit': 'PCS', 'user_id': 1}

    def test_if_user_is_anonymous_returns_401(self, create_product):
        response = create_product(self.sample_product)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_valid_returns_201(self, authenticate, create_product):
        user = get_user_model().objects.create()
        authenticate(id=user.id)

        response = create_product(
            {**self.sample_product, 'user_id': user.id})

        assert response.status_code == status.HTTP_201_CREATED

    def test_if_user_is_valid_but_data_is_invalid_returns_400(self, authenticate, create_product):
        user = get_user_model().objects.create()
        authenticate(id=user.id)

        response = create_product(
            {'user_id': user.id, **self.sample_product, 'name': ''})

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestRetrieveProduct:
    def test_if_product_exists_returns_200(self, api_client):
        user = get_user_model().objects.create()

        product = baker.make(Product, user_id=user.id)

        response = api_client.get(f'/invoicing/products/{product.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'id': product.id,
            'name': product.name,
            'unit': product.unit,
            'price': product.price,
            'user': user.id,
            'tax': product.tax,
            'stock': [],
            'hsn': None
        }


@pytest.mark.django_db
class TestRetrieveProducts:
    def test_if_products_list_endpoint_returns_200(self, api_client):
        user = get_user_model().objects.create()

        baker.make(Product, user_id=user.id, _quantity=10)

        response = api_client.get(f'/invoicing/products/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 10


@pytest.mark.django_db
class TestUpdateProduct:
    def test_if_user_is_anonymous_returns_401(self, create_product):
        response = create_product({'name': 'a', 'price': 10,
                                   'tax': 10, 'unit': 'PCS', 'user_id': 1})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_data_is_valid_returns_200(self, authenticate, api_client):
        user = get_user_model().objects.create()

        authenticate(id=user.id)

        product = baker.make(Product, user_id=user.id, hsn="")

        response = api_client.put(
            f'/invoicing/products/{product.id}/', {**product.__dict__, 'name': 'a'})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'a'
