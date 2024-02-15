from django.db import models
from utilities.generator import id_generator
from users.models import User

class Client(models.Model):
    "The client model. Which is also a subclass of the Base User class"
    id = models.CharField(primary_key=True, default=id_generator, editable=False, max_length=64)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="client_profile")
    about = models.TextField(max_length=1500, default='')

    city = models.CharField(default='', blank=True, max_length=100)
    phone = models.CharField(max_length=50, default='', blank=True)
    region = models.CharField(max_length=50, default='', blank=True)
    address = models.CharField(max_length=120, default='', blank=True)
    country = models.CharField(default='', max_length=100)
    zip_code = models.CharField(max_length=20, default='00000', blank=True)

    jobs_created = models.IntegerField(default=0)
    jobs_completed = models.IntegerField(default=0)


    def __str__(self):
        return self.user.username or self.country