from decimal import Decimal


def calculate_total_cost(item):
    total = item.price * item.quantity
    if item.packing_charges:
        total += item.packing_charges
    if item.discount >= 100:
        item.discount = 100
    total = total - round(Decimal(item.discount / 100), 2) * total
    return round(total, 2)


def calculate_total_tax(item):
    total = calculate_total_cost(item)
    return round(total * item.product.tax / 100, 2)
