from django.db import models


class Pricing(models.Model):
    budget = models.DecimalField(decimal_places=2, max_digits=10)

    fixed_price = models.BooleanField(
        default=True,
        blank=True,
        help_text="fixed price? If not, the price will be negotiable.",
    )

    negotiable_price = models.BooleanField(
        default=False, blank=True, help_text="open to negotiate the price?"
    )

    will_pay_more = models.BooleanField(
        default=False,
        blank=True,
        help_text="willing to pay more than the budget?",
    )

    addition_node = models.CharField(
        max_length=100,
        help_text="any additional information regarding the payment.",
    )

    payment_type = models.CharField(
        max_length=100,
        default="PROJECT",
        help_text="payment type. project or hourly.",
    )

    def __str__(self):
        return f"{self.payment_type} | Fixed: {self.fixed_price}"
