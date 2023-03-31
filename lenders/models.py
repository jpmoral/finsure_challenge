from decimal import Decimal

from django.db import models


class Lender(models.Model):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=150)
    upfront_commission = models.DecimalField(max_digits=7, decimal_places=4)
    high_trail_commission = models.DecimalField(max_digits=7, decimal_places=4)
    low_trail_commission = models.DecimalField(max_digits=7, decimal_places=4)
    is_active = models.BooleanField(default=True)
    is_hidden = models.BooleanField(default=False)
    balance_multiplier = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0.0'))
