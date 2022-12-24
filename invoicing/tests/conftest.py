import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticate(api_client):
    def do_authentication(is_staff=False, **data):
        return api_client.force_authenticate(user=User(is_staff=is_staff, **data))
    return do_authentication
