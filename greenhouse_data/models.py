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
        User, null=True, on_delete=models.SET_NULL, related_name="greenhouses")
    greenhouseUID = models.UUIDField(primary_key=True, default=uuid.uuid4)
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
    itemName = models.CharField(max_length=64)  # The name of the model
    # The identifiction of the models
    realSensorID = models.CharField(max_length=32)
    realSensorKey = models.CharField(
        max_length=32)  # The type fo the real sensor
    electricity = models.FloatField(default=100)
    lat = models.FloatField(null=True)
    lng = models.FloatField(null=True)


class SensorModel(models.Model):
    """
    The model for unit sensor instance
    """

    class Meta:
        db_table = "sensorTable"

    realSensor = models.ForeignKey(
        RealSensorModel, on_delete=models.CASCADE, related_name="sensors")
    itemName = models.CharField(max_length=64)
    # The sensor key would not duplicate in one real sensor
    sensorKey = models.CharField(max_length=32)


class ControllerModel(models.Model):
    """
    The model for unit controller instance
    """

    class Meta:
        db_table = "controllerTable"

    greenhouse = models.ForeignKey(
        GreenhouseModel, on_delete=models.CASCADE, related_name="controllers")
    itemName = models.CharField(max_length=64)
    controllerID = models.CharField(max_length=64)
    controllerKey = models.CharField(max_length=32)
    electricity = models.FloatField(default=100)
    lat = models.FloatField(null=True)
    lng = models.FloatField(null=True)


class SensorValueHistoryModel(models.Model):
    """
    Record sensor data history
    """
    class Meta:
        db_table = "sensorHistoryTable"
        ordering = ["sensor", "timestamp"]

    sensor = models.ForeignKey(
        SensorModel, on_delete=models.SET_NULL, null=True, related_name="sensorHistory")
    timestamp = models.DateTimeField()
    isCurrent = models.BooleanField(default=True)
    value = models.FloatField()


class ControllerSettingHistoryModel(models.Model):
    """
    Record controller setting history
    """

    class Meta:
        db_table = "controllerHistoryTable"
        ordering = ["controller", "timestamp"]

    controller = models.ForeignKey(
        ControllerModel, on_delete=models.CASCADE, related_name="controllerHistory")
    timestamp = models.DateTimeField()
    isCurrent = models.BooleanField(default=True)
    on = models.BooleanField()
    manualControl = models.BooleanField(default=False)
    openTemp = models.FloatField(null=True)
    closeTemp = models.FloatField(null=True)
    cutHumidity = models.FloatField(null=True)


class ScheduleModel(models.Model):
    """
    The model for each time schedule setting for electric vale
    """

    class Meta:
        db_table = "schedulesTable"

    controllerSetting = models.ForeignKey(
        ControllerSettingHistoryModel, on_delete=models.CASCADE, related_name="schedules")
    duration = models.DurationField()
    startTime = models.TimeField(default=datetime.time(16, 0, 0))
