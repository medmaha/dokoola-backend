from django.db import models


class UserPaymentMethod(models.Model):
    card_number = models.CharField(
        max_length=16,
        help_text="The card number for the payment method.",
    )
    card_holder_name = models.CharField(
        max_length=255,
        help_text="The name of the cardholder.",
    )
    expiration_date = models.DateField(
        help_text="The expiration date of the card.",
    )
    cvv = models.CharField(
        max_length=4,
        help_text="The CVV code of the card.",
    )
    is_default = models.BooleanField(
        default=False,
        help_text="Indicates if this is the default payment method.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.card_holder_name} - {self.card_number[-4:]}"


class UserBillingInfo(models.Model):
    address_line_1 = models.CharField(
        max_length=255,
        help_text="The first line of the billing address.",
    )
    address_line_2 = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="The second line of the billing address (optional).",
    )
    city = models.CharField(
        max_length=100,
        help_text="The city of the billing address.",
    )
    state = models.CharField(
        max_length=100,
        help_text="The state or region of the billing address.",
    )
    postal_code = models.CharField(
        max_length=20,
        help_text="The postal code of the billing address.",
    )
    country = models.CharField(
        max_length=100,
        help_text="The country of the billing address.",
    )
    phone_number = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        help_text="The phone number associated with the billing information.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserSecuritySettings(models.Model):
    class PasswordResetPeriodChoices(models.TextChoices):
        NEVER = "NEVER"
        EVERY_YEAR = "EVERY_YEAR"
        EVERY_MONTH = "EVERY_MONTH"
        EVERY_3_MONTHS = "EVERY_3_MONTHS"
        EVERY_6_MONTHS = "EVERY_6_MONTHS"
        EVERY_9_MONTHS = "EVERY_9_MONTHS"

    class FailedLoginAttempsChoices(models.IntegerChoices):
        UNLIMITED = 0
        THREE_ATTEMPS = 3
        FIVE_ATTEMPS = 5
        TEN_ATTEMPS = 10

    tfa_enabled = models.BooleanField(
        default=False, help_text="Two-Factor Authentication"
    )
    # tfa_qr_code = models.CharField(
    #     max_length=255,
    #     null=True,
    #     blank=True,
    # )
    # tfa_token = models.CharField(
    #     max_length=255,
    #     null=True,
    #     blank=True,
    # )

    session_timeout = models.CharField(
        null=True,
        max_length=50,
        help_text="Automatically log out after a period of inactivity.",
    )
    login_otifications = models.BooleanField(
        default=True,
        null=True,
        help_text="Receive notifications when a new login is detected on your account.",
    )
    multiple_sessions = models.BooleanField(
        null=True,
        default=False,
        help_text="Allow your account to be logged in on multiple devices simultaneously.",
    )
    failed_login_attemp = models.IntegerField(
        null=True,
        choices=FailedLoginAttempsChoices.choices,
        default=FailedLoginAttempsChoices.UNLIMITED,
        help_text="Limit the number of failed login attempts before locking the account.",
    )
    password_reset_period = models.CharField(
        null=True,
        max_length=50,
        default=PasswordResetPeriodChoices.NEVER,
        choices=PasswordResetPeriodChoices.choices,
        help_text="Require users to reset their password after a certain period.",
    )
    ip_restriction = models.BooleanField(
        null=True,
        default=False,
        help_text="Restrict access to your account from specific IP addresses.",
    )
    ip_whitelist = models.TextField(
        null=True, blank=True, help_text="IP addresses to allow."
    )


class UserPrivacySettings(models.Model):
    class ProfileVisibilityChoices(models.TextChoices):
        PUBLIC = "PUBLIC"
        PRIVATE = "PRIVATE"
        CONTACTS = "CONTACTS"

    profile_visiblity = models.CharField(
        max_length=50,
        choices=ProfileVisibilityChoices.choices,
        default=ProfileVisibilityChoices.PUBLIC,
        help_text="Control who can see your profile information.",
    )
    online_status = models.BooleanField(
        default=True, help_text="Show when you are online to others."
    )
    last_seen = models.BooleanField(
        default=True, help_text="Show when you were last active on the platform."
    )
    seo_indexing = models.BooleanField(
        default=False, help_text="Allow search engines to index your profile."
    )
    show_earnings = models.BooleanField(
        default=False, help_text="Display your earnings on your public profile."
    )


class UserNotificationSetting(models.Model):
    class NotificationDeliveryMethodChoices(models.TextChoices):
        BOTH = "BOTH"
        PUSH_NOTIFICATION = "PUSH_NOTIFICATION"
        EMAIL_NOTOFICATION = "EMAIL_NOTOFICATION"

    payments = models.BooleanField(
        default=True, help_text="Receive notifications about payments and transactions."
    )
    messages = models.BooleanField(
        default=True, help_text="Receive notifications for new messages."
    )
    new_proposal = models.BooleanField(
        default=True, help_text="Receive notifications when you get new proposals."
    )
    job_updates = models.BooleanField(
        default=True, help_text="Receive notifications about job status changes."
    )
    email_newsletter = models.BooleanField(
        default=True, help_text="Receive marketing emails and newsletters."
    )
    notification_delivery_method = models.CharField(
        max_length=255,
        default=NotificationDeliveryMethodChoices.BOTH,
        choices=NotificationDeliveryMethodChoices.choices,
    )


class UserSettings(models.Model):
    user = models.OneToOneField("users.User", on_delete=models.CASCADE)

    class LanguageTypeChoices(models.TextChoices):
        ENGLISH = "EN", "English"
        FRENCH = "FR", "French"
        SPANISH = "ES", "Spanish"
        PORTUGUESE = "PT", "Portuguese"

    class CurrencyTypeChoices(models.TextChoices):
        GMD = "GMD", "Gambian Dalasis"
        GBP = "CFA", "CFA Franc"
        USD = "USD", "US Dollar"
        EUR = "EUR", "Euro"

    updated_at = models.DateTimeField(auto_now=True)

    preferred_language = models.CharField(
        null=True,
        max_length=10,
        choices=LanguageTypeChoices.choices,
        default=LanguageTypeChoices.ENGLISH,
    )
    preferred_currency = models.CharField(
        null=True,
        max_length=10,
        default=CurrencyTypeChoices.GMD,
        choices=CurrencyTypeChoices.choices,
    )

    billing_info = models.OneToOneField(
        UserBillingInfo,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="user_preference",
    )
    payment_methods = models.ManyToManyField(
        UserPaymentMethod,
        blank=True,
        related_name="user_preference",
    )
    privacy_settings = models.OneToOneField(
        UserPrivacySettings,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="user_preference",
    )
    security_settings = models.OneToOneField(
        UserSecuritySettings,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="user_preference",
    )
    notification_settings = models.OneToOneField(
        UserNotificationSetting,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="user_preference",
    )

    def __str__(self):
        return f"[{self.user.username}'s] Preferences"

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.privacy_settings = UserPrivacySettings.objects.create()
            self.security_settings = UserSecuritySettings.objects.create()
            self.notification_settings = UserNotificationSetting.objects.create()
        return super().save(*args, **kwargs)
