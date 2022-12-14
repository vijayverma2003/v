from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from .validators import validate_file_size


class Firm(models.Model):
    name = models.CharField(max_length=255)
    gstin = models.CharField(max_length=55, null=True, blank=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class FirmLogo(models.Model):
    firm = models.OneToOneField(Firm,
                                primary_key=True, on_delete=models.CASCADE, related_name='logo')
    image = models.ImageField(upload_to='invoicing/images',
                              validators=[validate_file_size])


class Address(models.Model):
    street = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=55)
    state = models.CharField(max_length=55)
    country = models.CharField(max_length=55)
    firm = models.OneToOneField(
        Firm, on_delete=models.CASCADE, primary_key=True)


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(1)])
    tax = models.DecimalField(max_digits=4, decimal_places=2)
    unit = models.CharField(max_length=3)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ['name']


class Stock(models.Model):
    value = models.PositiveIntegerField()
    added_on = models.DateField(auto_now=True)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='stock')


class Customer(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=55)
    email = models.EmailField(max_length=55)
    gstin = models.CharField(max_length=55, null=True, blank=True)
    street = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=55)
    state = models.CharField(max_length=55)
    country = models.CharField(max_length=55)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name


class Transport(models.Model):
    name = models.CharField(max_length=255)
    mode = models.CharField(max_length=55)
    transporter_id = models.CharField(max_length=55)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name + ' - ' + self.transporter_id


class Invoice(models.Model):
    number = models.CharField(max_length=55)
    date = models.DateField()
    due_date = models.DateField()
    terms = models.TextField(
        max_length=2000, blank=True, default='')
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    transport = models.ForeignKey(
        Transport, on_delete=models.PROTECT, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    firm = models.ForeignKey(Firm, on_delete=models.CASCADE)


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name='invoiceitems')
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name='product')
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(1)])
    discount = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)], default=0)
    packing_charges = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    quantity = models.PositiveBigIntegerField()


class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    datetime = models.DateTimeField(auto_now_add=True)
    mode = models.CharField(max_length=55)
