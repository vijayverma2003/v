from decimal import Decimal


def calculate_total_cost(item):
    total = item.price * item.quantity
    return total - round(Decimal(item.discount / 100), 2) * total


def calculate_total_tax(item):
    total = calculate_total_cost(item)
    return total * item.product.tax / 100

