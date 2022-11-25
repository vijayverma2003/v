from rest_framework import serializers
from .models import Product, Stock


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    # price_with_tax = serializers.SerializerMethodField(
    #     method_name='calculate_tax')
    stock = StockSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'tax', 'stock']

    def calculate_tax(self, product: Product):
        return product.price + product.price * (product.tax / 100)
