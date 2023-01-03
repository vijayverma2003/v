import pytest
from invoicing.models import Product, Stock
from model_bakery import baker
from rest_framework import status


@pytest.fixture
def create_stock(api_client):
    def do_create_stock(product_id, stock):
        return api_client.post(f'/invoicing/products/{product_id}/stock/', stock)
    return do_create_stock


@pytest.mark.django_db
class TestCreateStock:
    def test_if_user_is_anonymous_returns_401(self, create_stock):
        product = baker.make(Product)
        response = create_stock(product.id, {'value': 100})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_and_data_is_valid_returns_201(self, authenticate, create_stock):
        product = baker.make(Product)
        authenticate()

        response = create_stock(product.id, {'value': 100})

        assert response.status_code == status.HTTP_201_CREATED

    def test_if_data_is_invalid_returns_400(self, authenticate, create_stock):
        product = baker.make(Product)
        authenticate()

        response = create_stock(product.id, {'value': -1})

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestRetrieveStock:
    def test_if_stock_exists_returns_200(self, api_client):
        stock = baker.make(Stock)

        response = api_client.get(
            f'/invoicing/products/{stock.product_id}/stock/{stock.id}/')

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestRetrieveStockList:
    def test_if_stock_exists_returns_200(self, api_client):
        product = baker.make(Product)
        stock = baker.make(Stock, product_id=product.id, _quantity=10)

        response = api_client.get(
            f'/invoicing/products/{product.id}/stock/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 10


@pytest.mark.django_db
class TestUpdateStock:
    def test_if_user_is_anonymous_returns_401(self, create_stock):
        product = baker.make(Product)
        response = create_stock(product.id, {'value': 100})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_data_is_valid_returns_200(self, api_client, authenticate):
        authenticate()
        stock = baker.make(Stock)

        response = api_client.put(
            f'/invoicing/products/{stock.product_id}/stock/{stock.id}/', {'value': 0})

        assert response.status_code == status.HTTP_200_OK
