from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=4, decimal_places=2)
    unit = models.CharField(max_length=3)


class Stock(models.Model):
    value = models.IntegerField()
    added_on = models.DateField(auto_now=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class Customer(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=55)
    email = models.EmailField(max_length=55)


class CustomerAddress(models.Model):
    street = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=55)
    state = models.CharField(max_length=55)
    country = models.CharField(max_length=55)
    customer = models.OneToOneField(
        Customer, on_delete=models.CASCADE, primary_key=True)


class Invoice(models.Model):
    number = models.CharField(max_length=55)
    date = models.DateField()
    due_date = models.DateField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    terms = models.TextField(max_length=2000)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)


class InvoiceProduct(models.Model):
    invoice = models.OneToOneField(
        Invoice, on_delete=models.CASCADE, primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.FloatField()
    packing_charges = models.DecimalField(max_digits=3, decimal_places=2)
    quantity = models.PositiveBigIntegerField()


class Transport(models.Model):
    invoice = models.OneToOneField(
        Invoice, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=255)
    mode = models.CharField(max_length=55)
    transporter_id = models.CharField(max_length=55)


class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    datetime = models.DateTimeField(auto_now_add=True)
    mode = models.CharField(max_length=55)
