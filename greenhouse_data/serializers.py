from datetime import datetime, timedelta

from django.contrib.auth.models import User
from rest_framework import serializers
from greenhouse_data.models import *

# TODO: solve foreign key issue with nested serializer


class EValveScheduleSerializer(serializers.ModelSerializer):
    """
    Convert json data to evalve schedule instance / convert evalve schedule instance into dictionary
    #### Request format:
    {
        "evalveProperty": the parent evalve property instance, (opt)
        "cutHumidity": float,
        "duration": int,
        "startTimeStr": isoformat time (HH:MM)
    }
    """

    startTime = serializers.TimeField(input_formats=["%H:%M"])

    class Meta:
        model = EvalveScheduleModel
        exclude = ["evalveProperty"]

    def create(self, validated_data):
        validated_data["duration"] = timedelta(
            seconds=validated_data["duration"])
        return EvalveScheduleModel.objects.create(**validated_data)


class EValvePropertySerializer(serializers.ModelSerializer):
    """
    Convert json data to evalve property instance / convert evalve property instance into dictionary
    #### Request format:
    {
        "controller": Controller instance, (opt)
        "evalveSchedule": list<map> instance for many EvalveScheduleModels
    }
    """
    evalveSchedules = EValveScheduleSerializer(many=True)

    class Meta:
        model = EvalvePropertyModel
        exclude = ["controller"]

    def create(self, validated_data):
        evalveSchedulesData = validated_data.pop("evalveSchedules")
        evalveProperty = EvalvePropertyModel.objects.create(**validated_data)

        evalveScheduleSerializer = self.fields["evalveSchedules"]
        for schedule in evalveSchedulesData:
            schedule["evalveProperty"] = evalveProperty
        evalveScheduleSerializer.create(evalveSchedulesData)

        return evalveProperty


class ShadePropertySerializer(serializers.ModelSerializer):
    """
    Convert json data to shade property instance / convert shade property instance into dictionary
    #### Request format:
    {
        "controller": Controller instance, (opt)
        "openTemp": float,
        "closeTemp": float,
    }
    """

    class Meta:
        model = ShadePropertyModel
        exclude = ["controller"]

    def create(self, validated_data):
        return super().create(validated_data)


class FanPropertySerializer(serializers.ModelSerializer):
    """
    Convert json data to fan property instance / convert fan property instance into dictionary
    #### Request format:
    {
        "controller": Controller instance, (opt)
        "openTemp": float,
        "closeTemp": float,
    }
    """

    class Meta:
        model = FanPropertyModel
        exclude = ["controller"]

    def create(self, validated_data):
        return super().create(validated_data)


class ControllerSerializer(serializers.ModelSerializer):
    """
    Convert json data to controller instance / convert controller instance into dictionary
    #### Request format:
    {
        "on": bool,
        "manual": bool,
        "parentItem": parent instance (opt)
        "evalveProperty": map instance,
        "shadeProperty": map instance,
        "fanProperty": map instance,
    }
    """
    evalveProperty = EValvePropertySerializer(many=False, allow_null=True)
    shadeProperty = ShadePropertySerializer(many=False, allow_null=True)
    fanProperty = FanPropertySerializer(many=False, allow_null=True)

    class Meta:
        model = ControllerModel
        exclude = ['parentItem']

    def validate(self, attrs):
        attrs = super().validate(attrs)
        tot = 0
        for key in ["evalveProperty", "shadeProperty", "fanProperty"]:
            if attrs[key] != None:
                tot += 1
        if tot > 1:
            raise serializers.ValidationError(
                {"there should be only one kind of property map"})
        elif tot < 1:
            raise serializers.ValidationError(
                {"there should be at least one kind of property map"})
        return attrs

    def create(self, validated_data):
        evalvePropertyData = validated_data.pop("evalveProperty")
        shadePropertyData = validated_data.pop("shadeProperty")
        fanPropertyData = validated_data.pop("fanProperty")

        controller = ControllerModel.objects.create(**validated_data)

        if (evalvePropertyData != None):
            evalvePropertySer = self.fields["evalveProperty"]
            evalvePropertyData["controller"] = controller
            evalvePropertySer.create(evalvePropertyData)

        elif (shadePropertyData != None):
            shadePropertySer = self.fields["shadeProperty"]
            shadePropertyData["controller"] = controller
            shadePropertySer.create(shadePropertyData)

        elif (fanPropertyData != None):
            fanPropertySer = self.fields["fanProperty"]
            fanPropertyData["controller"] = controller
            fanPropertySer.create(fanPropertyData)

        return controller


class SensorSerializer(serializers.ModelSerializer):
    """
    Convert json data to Sensor instance / convert sensor instance into dictionary
    #### Request format:
    {
        "parentItem": instance of parent item (opt)
        "currentValue": float,
    }
    """
    class Meta:
        model = SensorModel
        exclude = ['parentItem']

    def create(self, valData):
        sensor = SensorModel.objects.create(**valData)
        return sensor


class RealControllerSerializer(serializers.ModelSerializer):
    """
    Convert json data to realController instance / Convert realController instance into dictionary
    #### Request format:
    {
        greenhouse: instance of parent greenhouse (opt)
        nameKey: models.CharField(max_length=64)
        electricity: models.FloatField()
        lat: models.FloatField()
        lng :models.FloatField()

    }
    """
    controllers = ControllerSerializer(many=True)

    class Meta:
        model = RealControllerModel
        exclude = ["greenhouse"]

    def create(self, validated_data):
        contrlsValData = validated_data.pop('controllers')
        realController = RealControllerModel.objects.create(**validated_data)

        contrlSerializer = self.fields['controllers']
        for contrl in contrlsValData:
            contrl["parentItem"] = realController
        contrlSerializer.create(contrlsValData)

        return realController

    # TODO: not changed yet
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class RealSensorSerializer(serializers.ModelSerializer):
    """
    Convert json data to realSensor instance / Convert realSensor instance into dictionary
    #### Request format:
    {
        greenhouse: instance of parent greenhosue (opt)
        nameKey: models.CharField(max_length=64)
        electricity: models.FloatField()
        lat: models.FloatField()
        lng :models.FloatField()

    }
    """
    sensors = SensorSerializer(many=True, allow_empty=True)

    class Meta:
        model = RealSensorModel
        exclude = ["greenhouse"]

    def create(self, validated_data):
        sensorsValData = validated_data.pop('sensors')
        realSensor = RealSensorModel.objects.create(**validated_data)

        sensorsSerializer = self.fields['sensors']
        for sensor in sensorsValData:
            sensor["parentItem"] = realSensor
        sensorsSerializer.create(sensorsValData)

        return realSensor

    # TODO: not changed yet
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class GreenhouseSerializer(serializers.ModelSerializer):
    """
    Convert json data to greenhouse instance / Convert greenhouse instance into dictionary
    #### Request format:
    {
        'owner': username,
        'name': str,
        "address": str,
        "beginDateStr": str,
        "realSensors": list<dict>,
        "realControllers": list<dict>,
    }
    """

    # TODO: add real sensor and real controller later
    """
    Note:
        - JSON: give an owner primary key -> owner instance is given in validated_data
        - Instance: give an owner(user) instance -> user id is given in validated_data (?)
    """
    owner = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=False,
    )
    realSensors = RealSensorSerializer(many=True, allow_empty=True)
    realControllers = RealControllerSerializer(many=True, allow_empty=True)
    beginDate = serializers.DateField(
        format="%Y-%m-%d", input_formats="%Y-%m-%d")

    class Meta:
        model = GreenhouseModel
        fields = ['owner', 'name', 'address',
                  'beginDate', 'realSensors', 'realControllers']

    # TODO: not changed yet
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def create(self, validated_data):
        # pop out real_sensors dictionary
        realSensorDatas = validated_data.pop('realSensors')
        # pop out real_controller dictionary
        realControllerDatas = validated_data.pop('realControllers')

        beginDate = datetime.fromisoformat(validated_data['beginDateStr'])
        greenhouse = GreenhouseModel.objects.create(
            owner=validated_data['owner'],
            name=validated_data['name'],
            address=validated_data['address'],
            beginDate=beginDate,
        )

        # create real sensors
        realSensorSerializer = self.fields['realSensors']
        for rSensor in realSensorDatas:
            rSensor["greenhouse"] = greenhouse

        realSensorSerializer.create(realSensorDatas)

        # create real controllers
        realControllerSerializer = self.fields['realControllers']
        for rController in realControllerDatas:
            rController["greenhouse"] = greenhouse

        realControllerSerializer.create(realControllerDatas)

        return greenhouse
