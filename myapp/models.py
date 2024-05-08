from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.


class Customer(User):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phoneNumber = PhoneNumberField(null=False, blank=False, unique=True)
    email = models.EmailField(null=True)
