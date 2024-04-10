import uuid
import datetime
from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class GreenhouseModel(models.Model):
    """
    The model for greenhosue main information
    """
    class Meta:
        db_table = "greenhouseTable"
        ordering = ["owner", "-beginDate"]

    owner = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name="greenhouse")
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=32)
    address = models.CharField(max_length=128)
    beginDate = models.DateField()  # format YYYY-MM-DD
    photo = models.ImageField(
        "Greenhouse Avatar", upload_to="image/greenhouse_photo", null=True)

    def __str__(self) -> str:
        return super().__str__()


class RealSensorModel(models.Model):
    """
    The model for real sensor item
    """
    class Meta:
        db_table = "realSensorTable"

    greenhouse = models.ForeignKey(
        GreenhouseModel, on_delete=models.CASCADE, related_name="realSensors")
    uid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    nameKey = models.CharField(max_length=64)
    electricity = models.FloatField()
    lat = models.FloatField()
    lng = models.FloatField()


class RealControllerModel(models.Model):
    """
    The model for real controller item
    """
    class Meta:
        db_table = "realControllerTable"

    greenhouse = models.ForeignKey(
        GreenhouseModel, on_delete=models.CASCADE, related_name="realControllers")
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    nameKey = models.CharField(max_length=64)
    electricity = models.FloatField()
    lat = models.FloatField()
    lng = models.FloatField()


class SensorModel(models.Model):
    """
    The model for unit sensor instance
    """

    class Meta:
        db_table = "sensorTable"

    parentItem = models.ForeignKey(
        RealSensorModel, on_delete=models.CASCADE, related_name="sensors")
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    currentValue = models.FloatField()


class ControllerModel(models.Model):
    """
    The model for unit controller instance
    """

    class Meta:
        db_table = "controllerTable"

    parentItem = models.ForeignKey(
        RealControllerModel, on_delete=models.CASCADE, related_name="controllers")
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    on = models.BooleanField()
    manual = models.BooleanField()


class EvalvePropertyModel(models.Model):
    """
    The model especially for electric valve property except for the scheduled time slots.
    """
    # NOTE: this model currently contains nothing
    class Meta:
        db_table = "evalvePropertyTable"

    controller = models.OneToOneField(
        ControllerModel, on_delete=models.CASCADE, primary_key=True, related_name="evalveProperty")


class EvalveScheduleModel(models.Model):
    """
    The model for each time schedule setting for electric vale
    """

    class Meta:
        db_table = "evalveScheduleTable"

    evalveProperty = models.ForeignKey(
        EvalvePropertyModel, on_delete=models.CASCADE, related_name="evalveSchedules")
    cutHumidity = models.FloatField()
    duration = models.DurationField()
    startTime = models.TimeField(default=datetime.time(0, 0, 0))


class ShadePropertyModel(models.Model):
    """
    The model especially for shade controller property
    """
    class Meta:
        db_table = "shadePropertyTable"

    controller = models.OneToOneField(
        ControllerModel, on_delete=models.CASCADE, primary_key=True, related_name="shadeProperty")
    openTemp = models.FloatField()
    closeTemp = models.FloatField()


class FanPropertyModel(models.Model):
    """
    The model especially for fan controller property
    """
    class Meta:
        db_table = "fanPropertyTable"

    controller = models.OneToOneField(
        ControllerModel, on_delete=models.CASCADE, primary_key=True, related_name="fanProperty")
    openTemp = models.FloatField()
    closeTemp = models.FloatField()
