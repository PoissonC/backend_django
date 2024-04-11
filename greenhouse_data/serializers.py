from datetime import datetime, timedelta

from django.contrib.auth.models import User
from rest_framework import serializers
from greenhouse_data.models import *

# TODO: update to time table database form


class SensorValueHistorySerializer(serializers.ModelSerializer):
    """
    Convert json data to sensor value history instance / convert sensor value history instance into dictionary
    """

    class Meta:
        model = SensorValueHistoryModel
        fields = ["timeStamp", "isCurrent", "value"]


class EValveScheduleSerializer(serializers.ModelSerializer):
    """
    Convert json data to evalve schedule instance / convert evalve schedule instance into dictionary
    """

    class Meta:
        model = EvalveScheduleModel
        # generally controllerSetting is also required for creation
        fields = ["cutHumidity", "duration", "startTime"]


class ControllerSerializer(serializers.ModelSerializer):
    """
    Convert json data to controller instance
    """

    timestamp = serializers.DateTimeField()
    on = serializers.BooleanField(allow_null=True, required=False)
    manualControl = serializers.BooleanField(allow_null=True, required=False)
    openTemp = serializers.FloatField(allow_null=True, required=False)
    closeTemp = serializers.FloatField(allow_null=True, required=False)
    evalveSchedules = EValveScheduleSerializer(
        many=True, allow_null=True, required=False)

    class Meta:
        model = ControllerModel
        fields = ["index", "controllerKey", "timestamp", "on", "manualControl",
                  "openTemp", "closeTemp", "evalvSchedules"]

    def validate(self, attrs):
        attrs = super().validate(attrs)

        keysMap = {
            "evalve": ["evalveSchedules"],
            "shade": ["openTemp", "closeTemp"],
            "fan": ["openTemp", "closeTemp"]
        }

        if attrs["controllerKey"] not in keysMap.keys:
            raise serializers.ValidationError({"controllerKey is not defined"})

        for controllerKey in keysMap.keys:
            if attrs["controllerKey"] == controllerKey:
                for requiredKey in keysMap[controllerKey]:
                    if attrs[requiredKey] is None:
                        raise serializers.ValidationError(
                            {f"'{requiredKey}' should not be None when 'controllerKey' is '{controllerKey}"})
        return attrs

    # UNDONE: not implemented yet
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def create(self, validated_data):
        """ The method is for the first declaration of the controller"""
        if validated_data["parentItem"] is None:
            raise serializers.ValidationError(
                {"parentItem parameter is required when creating controller instance"})

        controller = ControllerModel.objects.create(
            index=validated_data["index"],
            controllerKey=validated_data["controllerKey"],
            parentItem=validated_data["parentItem"],
        )
        controllerSetting = ControllerSettingHistoryModel.objects.create(
            controller=controller,
            timestamp=validated_data["timestamp"],
            on=validated_data["on"],
            manualControl=validated_data["manualControl"],
            openTemp=validated_data["openTemp"],
            closeTemp=validated_data["closeTemp"],
        )

        if validated_data["evalveSchedules"] is not None:
            eSchedulesData = validated_data["evalveSchedules"]
            eSer = self.fields["evalveSchedules"]
            for s in eSchedulesData:
                s["controllerSetting"] = controllerSetting
            eSer.create(eSchedulesData)
        return controller


class SensorSerializer(serializers.ModelSerializer):
    """
    Convert json data to Sensor instance
    """

    timestamp = serializers.DateTimeField()  # YYYY-MM-DD hh:mm:ss
    currentValue = serializers.FloatField()

    class Meta:
        model = SensorModel
        # normally "parentItem" is requested as well
        fields = ['index', 'sensorKey', 'currentValue', 'timestamp']

    # UNDONE: overwrite it when needed
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def create(self, valData):
        """ The method is for the first declaration of the sensor"""
        if valData["parentItem"] is None:
            raise serializers.ValidationError(
                {"parentItem parameter is required when creating Sensor instance"})

        sensor = SensorModel.objects.create(
            index=valData['index'],
            sensorKey=valData['sensorKey'],
            parentItem=valData["parentItem"],
        )
        SensorValueHistoryModel.objects.create(
            timestamp=valData["timestamp"],
            value=valData["currentValue"],
            sensor=sensor,
            isCurrent=True,
        )
        return sensor

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return ret


class RealControllerSerializer(serializers.ModelSerializer):
    """
    Convert json data to realController instance / Convert realController instance into dictionary
    """
    controllers = ControllerSerializer(many=True)

    class Meta:
        model = RealControllerModel
        fields = ["nameKey", "lat", "lng", "electricity", "controllers"]

    # UNDONE: not changed yet
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def create(self, validated_data):
        contrlsValData = validated_data.pop('controllers')
        realController = RealControllerModel.objects.create(**validated_data)

        contrlSerializer = self.fields['controllers']
        for contrl in contrlsValData:
            contrl["parentItem"] = realController
        contrlSerializer.create(contrlsValData)

        return realController


class RealSensorSerializer(serializers.ModelSerializer):
    """
    Convert json data to realSensor instance / Convert realSensor instance into dictionary
    """
    sensors = SensorSerializer(
        many=True, allow_empty=True, required=False)

    class Meta:
        model = RealSensorModel
        fields = ["nameKey", "lat", "lng", "electricity", "sensors"]

    # TODO: not changed yet
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def create(self, validated_data):
        sensorsValData = validated_data.pop('sensors')
        realSensor = RealSensorModel.objects.create(**validated_data)

        sensorsSerializer = self.fields['sensors']
        for sensor in sensorsValData:
            sensor["parentItem"] = realSensor
        sensorsSerializer.create(sensorsValData)

        return realSensor

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["uid"] = instance.uid
        return ret


class GreenhouseSerializer(serializers.ModelSerializer):
    """
    Convert json data to greenhouse instance / Convert greenhouse instance into dictionary
    """
    """
    Note:
        - JSON: give an owner primary key -> owner instance is given in validated_data
        - Instance: give an owner(user) instance -> user id is given in validated_data (?)
    """
    owner = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=False,
    )
    realSensors = RealSensorSerializer(
        many=True, allow_null=True, allow_empty=True, required=False)
    realControllers = RealControllerSerializer(
        many=True, allow_null=True, allow_empty=True, required=False)

    class Meta:
        model = GreenhouseModel
        fields = ['owner', 'name', 'address',
                  'beginDate', 'realSensors', 'realControllers']

    # UNDONE: not changed yet
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def create(self, validated_data):
        # pop out real_sensors dictionary
        realSensorDatas = validated_data.pop('realSensors')
        # pop out real_controller dictionary
        realControllerDatas = validated_data.pop('realControllers')

        greenhouse = GreenhouseModel.objects.create(**validated_data)

        # create real sensors
        realSensorSerializer = self.fields['realSensors']
        for rSensor in realSensorDatas:
            rSensor["greenhouse"] = greenhouse

        realSensorSerializer.create(realSensorDatas)

        # create real controllers
        realControllerSerializer = self.fields['realControllers']
        for rController in realControllerDatas:
            # NOTE: we can try using PrimaryKeyField for this kind of things, so we only has to input greenhouseUID instead of an instance
            rController["greenhouse"] = greenhouse

        realControllerSerializer.create(realControllerDatas)

        return greenhouse

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["uid"] = instance.uid

        return ret
