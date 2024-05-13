from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from .models import *
from phonenumber_field.serializerfields import PhoneNumberField


class UserInforSerializer(serializers.ModelSerializer):

    user = serializers.PrimaryKeyRelatedField(
        many=False, queryset=User.objects.all())
    phoneNumber = PhoneNumberField(
        allow_null=True, required=False)
    email = serializers.EmailField(allow_null=True, required=False)

    class Meta:
        model = UserInformationModel
        fields = ('user', 'phoneNumber', 'email', 'name')

    def create(self, validated_data):
        userInfoInstance = UserInformationModel.objects.create(
            user=validated_data["user"],
            phoneNumber=validated_data.setdefault("phoneNumber", None),
            Email=validated_data.setdefault("Email", None),
        )
        return userInfoInstance

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        user = User.objects.get(id=ret["user"])
        ret["username"] = user.username
        return ret


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password')

    def validate(self, data):

        # TODO: comment this line out for the validator is too annoying
        # validate_password(data['password'])
        return data

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
        )
        user.set_password(validated_data['password'])
        user.save()
        Token.objects.create(user=user)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value
