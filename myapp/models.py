from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.


class UserInfoModel(User):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_info", primary_key=True)
    phoneNumber = PhoneNumberField(null=True, blank=False, unique=True)
    Email = models.EmailField(null=True)
