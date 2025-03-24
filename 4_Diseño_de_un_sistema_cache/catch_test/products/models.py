from django.db import models

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    quantity = models.PositiveIntegerField(default=1)
    sku = models.IntegerField(blank=True, null=True, unique=True)

    def __str__(self):
        return self.name