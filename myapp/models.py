from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.


class UserInformationModel(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True)
    phoneNumber = PhoneNumberField(null=True, blank=False, unique=False)
    Email = models.EmailField(null=True)
