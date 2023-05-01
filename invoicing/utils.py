from decimal import Decimal
from num2words import num2words


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


def get_in_words(num, currency):
    first, second = str(num).split('.')

    first_to_words = num2words(first)

    num_to_words = first_to_words.capitalize(
    ) + f" {currency['name']}" + " and "

    if second != 0:
        second_to_words = num2words(second)
        num_to_words += second_to_words + \
            f" {currency['smaller_unit']}"

    return num_to_words
