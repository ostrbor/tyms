from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=64)


class Product(models.Model):
    category = models.ForeignKey(Category)
    name = models.CharField(max_length=128)
    price = models.DecimalField(max_digits=10, decimal_places=2)
