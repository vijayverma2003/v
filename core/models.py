from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)


class Currency(models.Model):
    name = models.CharField(max_length=55)
    symbol = models.CharField(max_length=1, null=True, blank=True)
    label = models.CharField(max_length=15)

    def __str__(self) -> str:
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=55)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    idd = models.CharField(max_length=15)
