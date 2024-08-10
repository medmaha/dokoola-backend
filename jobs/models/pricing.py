from django.db import models

class Pricing(models.Model):
    fixed_price = models.BooleanField(default=True, blank=True)
    negotiable_price = models.BooleanField(default=False, blank=True)
    will_pay_more = models.BooleanField(default=False, blank=True)
    addition = models.CharField(max_length=100)
    payment_type = models.CharField(max_length=100, default="PROJECT")
    deleted = models.BooleanField(default=False, blank=True)
