from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .serializers import CurrencySerializer, CountrySerializer, CreateCountrySerializer
from .models import Currency, Country
from rest_framework.permissions import IsAdminUser, AllowAny

# Create your views here.


class CurrencyViewSet(ModelViewSet):
    serializer_class = CurrencySerializer
    queryset = Currency.objects.all()

    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        else:
            return [IsAdminUser()]


class CountryViewSet(ModelViewSet):
    serializer_class = CountrySerializer
    queryset = Country.objects.all()

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        else:
            return [IsAdminUser()]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CountrySerializer
        else:
            return CreateCountrySerializer
