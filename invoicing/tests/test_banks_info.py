import pytest
from model_bakery import baker
from invoicing.models import Bank, Firm
from rest_framework import status


@pytest.fixture
def create_bank(api_client):
    def do_create_bank(firm_id, data):
        return api_client.post(f'/invoicing/firms/{firm_id}/bank/', data)
    return do_create_bank


@pytest.mark.django_db
class TestCreateBank:
    sample_data = {'name': 'a', 'ifsc': 'a',
                   'acc': 'a', 'branch': 'a'}

    def test_if_user_is_anonymous_returns_401(self, create_bank):
        firm = baker.make(Firm)

        response = create_bank(firm.id, self.sample_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_valid_returns_201(self, authenticate, create_bank):
        firm = baker.make(Firm)
        authenticate(firm.user_id)

        response = create_bank(firm.id, self.sample_data)

        assert response.status_code == status.HTTP_201_CREATED

    def test_if_data_is_invalid_returns_400(self, authenticate, create_bank):
        firm = baker.make(Firm)
        authenticate(firm.user_id)

        response = create_bank(firm.id, {**self.sample_data, 'name': ''})

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestRetrieveBank:
    def test_if_bank_info_exists_returns_200(self, api_client):
        bank = baker.make(Bank)

        response = api_client.get(
            f'/invoicing/firms/{bank.firm_id}/bank/{bank.firm_id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'name': bank.name,
            'ifsc': bank.ifsc,
            'acc': bank.acc,
            'branch': bank.branch
        }


@pytest.mark.django_db
class TestUpdateBank:
    def test_if_user_is_valid_returns_200(self, authenticate, api_client):
        bank = baker.make(Bank)
        print(bank.__dict__)
        authenticate(bank.firm.user.id)

        response = api_client.put(
            f'/invoicing/firms/{bank.firm_id}/bank/{bank.firm_id}/', {'name': 'a', 'ifsc': 'a',
                                                                      'acc': bank.acc, 'branch': "a"})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'a'
        assert response.data['ifsc'] == 'a'
        assert response.data['branch'] == 'a'
