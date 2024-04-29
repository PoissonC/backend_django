from datetime import datetime, timedelta

from django.contrib.auth.models import User
from rest_framework import serializers
from greenhouse_data.models import *

"""
The propose of the serializers is to
1. turn the json format into model intance
2. turn the model instance into json format
"""

# TODO: use only model to interact with the instance
# TODO: remove realController layer, the greenhouse will directly control all of the controller
# TODO: maybe seprate the serialier and deserializer

"""
Sensors
"""


class SensorValueHistorySerializer(serializers.ModelSerializer):
    """
    Convert json data to sensor value history instance / convert sensor value history instance into dictionary

    #### Input format
    ```
    {
        "sensor": sensorInstance,
        "value": 22,
        "timestamp": "2024-04-03 17:04:04",
    }
    ```
    """

    class Meta:
        model = SensorValueHistoryModel
        fields = '__all__'

    def __pushLastCurrent(self, sensor):
        sensorDatas = list(SensorValueHistoryModel.objects.filter(
            sensor=sensor, isCurrent=True))
        if (len(sensorDatas) == 0):
            return True
        if (len(sensorDatas) == 1):
            sensorDatas[0].isCurrent = False
            sensorDatas[0].save()
            return True
        if (len(sensorDatas) > 1):
            for setting in sensorDatas:
                setting.isCurrent = False
            print(
                "warning: multiple instances have isCurrent == True, something might went wrong")
            return True

    def create(self, validated_data):
        """
        Update sensor data is actually creating new sensor data history
        instance. In the `create` method from controller setting serializer,
        the last current data will be set to `isCurrent = False` automatically.
        """
        if validated_data["sensor"] is None:
            raise serializers.ValidationError(
                {"controller instance is not provided"})
        self.__pushLastCurrent(validated_data["sensor"])
        sensorData = SensorValueHistoryModel.objects.create(
            **validated_data)
        return sensorData

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return ret


class SensorSerializer(serializers.ModelSerializer):
    """
    Convert json data to Sensor instance

    #### Input format
    ```
    {
        "parentItem": realSensorInstance,
        "sensorKey": "airHumidity",
        "currentValue": 22,
        "timestamp": "2024-04-03 17:04:04",
    }
    ```

    #### Serialized format
    ```
    {
        "parentItem": realSensorInstance,
        "sensorKey": "airHumidity",
        "currentValue": 22,
    }
    ```
    """

    timestamp = serializers.DateTimeField()  # YYYY-MM-DD hh:mm:ss
    currentValue = serializers.FloatField()

    class Meta:
        model = SensorModel
        fields = '__all__'

    def create(self, valData):
        """ The method is for the first declaration of the sensor"""
        valData.setdefault("parentItem", None)
        if valData["parentItem"] is None:
            raise serializers.ValidationError(
                {"parentItem parameter is required when creating Sensor instance"})

        sensor = SensorModel.objects.create(
            sensorKey=valData.pop("sensorKey"),
            parentItem=valData.pop("parentItem"),
        )

        valData["sensor"] = sensor
        sensorValueSer = SensorValueHistorySerializer()
        sensorValueSer.create(valData)
        return sensor

    def to_representation(self, instance):
        ret = {
            "sensorKey": instance.sensorKey,
            "parentItem": instance.parentItem.id,
        }
        currentSensorData = list(SensorValueHistoryModel.objects.filter(
            sensor=instance).filter(isCurrent=True))
        if len(currentSensorData) == 0:
            ret["currentValue"] = None
            return ret
        ret["currentValue"] = currentSensorData[0].value

        return ret


class RealSensorSerializer(serializers.ModelSerializer):
    """
    Convert json data to realSensor instance / Convert realSensor instance into dictionary

    #### Json input format for serializer
    ```
    {
        "greenhouse": greenhouseInstance,
        "realSensorID": "airSensor", # originally the key of request data
        "electricity": 100,
        "lat": 24.112,
        "lng": 47.330,
        "sensors": {
            "airHumidity": {"value": 22, "timestamp": "2024-04-03 17:04:04"},
            "airTemp": {"value": 31, "timestamp": "2024-04-03 17:04:04"},
        }
    }
    ```

    #### Representation format
    ```
    {
        'id': 9,
        'realSensorID': 'AirSensor_0',
        'electricity': 88.2,
        'lat': 32.1,
        'lng': 18.3,
        'greenhouse': UUID('70c8a4d7-019e-433b-8491-200ef4a33d48'),
        'sensors': [
            {
                'sensorKey': 'airHumidity',
                'parentItem': realSensorInstance,
                'currentValue': 22.0
            },
            {
                'sensorKey': 'airTemp',
                'parentItem': realSensorInstance,
                'currentValue': 31.0
            }
        ],
    }
    ```
    """

    sensors = SensorSerializer(
        many=True, allow_empty=True, required=False)

    class Meta:
        model = RealSensorModel
        fields = '__all__'

    def __validate(self, validated_data):
        # validate id
        containedID = list(map(lambda x: x.realSensorID, RealSensorModel.objects.filter(
            greenhouse=validated_data["greenhouse"])))
        if validated_data["realSensorID"] in containedID:
            raise serializers.ValidationError(
                {"realSensorID existed in the greenhouse"})

    def create(self, validated_data):
        self.__validate(validated_data)
        sensorsValData: dict = validated_data.pop('sensors')
        realSensor = RealSensorModel.objects.create(**validated_data)

        sensorsSerializer = self.fields['sensors']
        sensorList = []
        for key, sensor in sensorsValData.items():
            sensor["parentItem"] = realSensor
            sensor["sensorKey"] = key
            sensorList.append(sensor)
        sensorsSerializer.create(sensorList)

        return realSensor

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return ret


"""
Controllers
"""


class EValveScheduleSerializer(serializers.ModelSerializer):
    """
    Convert json data to evalve schedule instance / convert evalve schedule instance into dictionary
    """

    duration = serializers.DurationField()

    class Meta:
        model = EvalveScheduleModel
        # generally controllerSetting is also required for creation
        fields = ["cutHumidity", "duration", "startTime"]

    def create(self, validated_data):
        validated_data["duration"] = datetime.timedelta(
            seconds=validated_data["duration"])
        instance = EvalveScheduleModel.objects.create(**validated_data)
        return instance


class ControllerSettingSerializer(serializers.ModelSerializer):
    """
    Convert jsoon data in to instance

    #### json input format
    ```
    {
        "controller": controllerInstance,
        "timestamp": "2024-04-03 17:04:04",
        "openTemp": 31.2, # ignored if not used
        "closeTemp": 30.1, # ignored if not used
        "evalveSchedules": [ # ignored if not used
            {"cutHumidity": 24.1, "duration": 15, "startTime": "15:00"},
            {"cutHumidity": 24.3, "duration": 15, "startTime": "12:00"}
        ]
    }
    ```
    """

    openTemp = serializers.FloatField(allow_null=True, required=False)
    closeTemp = serializers.FloatField(allow_null=True, required=False)
    evalveSchedules = EValveScheduleSerializer(
        many=True, allow_null=True, required=False)

    class Meta:
        model = ControllerSettingHistoryModel
        fields = '__all__'

    def __pushLastCurrent(self, controller):
        controllerSettings = list(ControllerSettingHistoryModel.objects.filter(
            controller=controller, isCurrent=True))
        if (len(controllerSettings) == 0):
            return True
        if (len(controllerSettings) == 1):
            controllerSettings[0].isCurrent = False
            controllerSettings[0].save()
            return True
        if (len(controllerSettings) > 1):
            for setting in controllerSettings:
                setting.isCurrent = False
            print(
                "warning: multiple instances have isCurrent == True, something might went wrong")
            return True

    def create(self, validated_data):
        """
        Update controller setting is actually creating new controller setting history
        data. In the `create` method from controller setting serializer, the last current
        data will be set to `isCurrent = False` automatically.
        """
        if validated_data["controller"] is None:
            raise serializers.ValidationError(
                {"controller instance is not provided"})
        self.__pushLastCurrent(validated_data["controller"])

        validated_data.setdefault("openTemp", None)
        validated_data.setdefault("closeTemp", None)
        validated_data.setdefault("evalveSchedules", None)
        evalveSchedulesData = validated_data.pop("evalveSchedules")

        controllerSetting = ControllerSettingHistoryModel.objects.create(
            **validated_data)

        if evalveSchedulesData is not None:
            eSer = self.fields["evalveSchedules"]
            for s in evalveSchedulesData:
                s["controllerSetting"] = controllerSetting
            eSer.create(evalveSchedulesData)

        return controllerSetting

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        schedules = list(EvalveScheduleModel.objects.filter(
            controllerSetting=instance))

        if len(schedules) != 0:
            ret["evalveSchedules"] = []
            for s in schedules:
                ser = EValveScheduleSerializer(s)
                ret["evalveSchedules"].append(ser.data)

        return ret


class ControllerSerializer(serializers.ModelSerializer):
    """
    Convert json data to controller instance

    #### Json input format for serializer
    ```
    {
        "greenhouse": greenhouseInstance,
        "controllerID": "Watering_1", # received from the key of request data
        "electricity": 100,
        "lat": 24.112,
        "lng": 47.330,
        # controller setting
        "setting": {
            "on": False,
            "manualControl": False,
            "timestamp": "2024-04-03 17:04:04",
            "openTemp": 31.2, # ignored if not used
            "closeTemp": 30.1, # ignored if not used
            "evalveSchedules": [ # ignored if not used
                {"cutHumidity": 24.1, "duration": 15, "startTime": "15:00"},
                {"cutHumidity": 24.3, "duration": 15, "startTime": "12:00"}
            ]
        }
    }
    ```

    #### Representation format
    ```
    {
        "greenhouse": greenhouseInstance,
        "controllerID": "watering_1", # originally the key of request data
        "controllerKey": "evalve",
        "electricity": 100,
        "lat": 24.112,
        "lng": 47.330,
        "setting": {
            "openTemp": 31.2, # ignored if not used
            "closeTemp": 30.1, # ignored if not used
            "evalveSchedules": [ # ignored if not used
                {"cutHumidity": 24.1, "duration": 15, "startTime": "15:00"},
                {"cutHumidity": 24.3, "duration": 15, "startTime": "12:00"}
            ]
        }
    }
    ```
    """

    setting = ControllerSettingSerializer()

    class Meta:
        model = ControllerModel
        fields = '__all__'

    def validate(self, attrs):
        attrs = super().validate(attrs)
        return attrs

    def __validate(self, validated_data):
        keysMap = {
            "evalve": ["evalveSchedules"],
            "shade": ["openTemp", "closeTemp"],
            "fan": ["openTemp", "closeTemp"]
        }
        # validate id
        containedID = list(map(lambda x: x.controllerID, ControllerModel.objects.filter(
            greenhouse=validated_data["greenhouse"])))
        if validated_data["controllerID"] in containedID:
            raise serializers.ValidationError(
                {"controllerID existed in the greenhouse"})

        if validated_data["controllerKey"] not in keysMap.keys():
            raise serializers.ValidationError({"controllerKey is not defined"})

        for requiredKey in keysMap[validated_data["controllerKey"]]:
            if validated_data["setting"][requiredKey] is None:
                raise serializers.ValidationError(
                    {f"'{requiredKey}' should not be None when 'controllerKey' is '{validated_data['controllerKey']}"})

    def create(self, validated_data):
        """
        The method is for the first declaration of the controller. The beginning setting
        would be labled "isCurrent" in controller setting history model. Only the latest
        setting would be labeled with "isCurrent == True" in ControllerSettingHistoryModel
        """
        self.__validate(validated_data)
        settingData = validated_data.pop("setting")

        controller = ControllerModel.objects.create(**validated_data)

        # create new controller
        settingData["controller"] = controller
        controllerSettingSer = self.fields["setting"]
        controllerSettingSer.create(settingData)

        return controller

    def to_representation(self, instance):
        """
        Get the current controller setting for the controller, serialzie the current controller setting
        to json format. The controller setting might include the following fields
        `["on", "manualControl", "openTemp", "closeTemp", "evalveSchedules]`
        """
        ret = {
            "greenhouse": instance.greenhouse.uid,
            "controllerID": instance.controllerID,
            "controllerKey": instance.controllerKey,
            "electricity": instance.electricity,
            "lat": instance.lat,
            "lng": instance.lng,
        }

        currentControllerSettingList = list(ControllerSettingHistoryModel.objects.filter(
            controller=instance).filter(isCurrent=True))

        if len(currentControllerSettingList) == 0:
            ret["setting"] = None
            return ret

        currentControllerSetting = currentControllerSettingList[0]
        cSettingSer = ControllerSettingSerializer(currentControllerSetting)
        ret["setting"] = cSettingSer.data
        return ret


"""
Greenhouse
"""


class GreenhouseSerializer(serializers.ModelSerializer):
    """
    Convert json data to greenhouse instance / Convert greenhouse instance into dictionary
    """
    """
    # NOTE:
        - JSON: give an owner primary key -> owner instance is given in validated_data
        - Instance: give an owner(user) instance -> user id is given in validated_data (?)
    """
    owner = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=False,
    )
    realSensors = RealSensorSerializer(
        many=True, allow_null=True, allow_empty=True, required=False)
    controllers = ControllerSerializer(
        many=True, allow_null=True, allow_empty=True, required=False)
    uid = serializers.UUIDField(required=False)

    class Meta:
        model = GreenhouseModel
        fields = '__all__'

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def create(self, validated_data):
        # pop out real_sensors dictionary
        realSensorDatas = validated_data.pop('realSensors')
        # pop out real_controller dictionary
        controllerDatas = validated_data.pop('controllers')

        greenhouse = GreenhouseModel.objects.create(**validated_data)

        # create real sensors
        realSensorSerializer = self.fields['realSensors']
        for rSensor in realSensorDatas:
            rSensor["greenhouse"] = greenhouse

        realSensorSerializer.create(realSensorDatas)

        # create real controllers
        controllerSerializer = self.fields['controllers']
        for controller in controllerDatas:
            # NOTE: we can try using PrimaryKeyField for this kind of things, so we only has to input greenhouseUID instead of an instance
            controller["greenhouse"] = greenhouse

        controllerSerializer.create(controllerDatas)

        return greenhouse

    def to_representation(self, instance: GreenhouseModel):
        ret = super().to_representation(instance)
        return ret
