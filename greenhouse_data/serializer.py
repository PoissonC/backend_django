from datetime import datetime, timedelta

from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.utils import html, model_meta, representation

from django.core.exceptions import ValidationError as DjangoValidationError
from greenhouse_data.models import *

"""
The propose of the serializers is to
1. turn the json format into model intance
2. turn the model instance into json format
"""

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
        if validated_data.setdefault("sensor", None) is None:
            raise serializers.ValidationError(
                {"sensor instance is not provided"})
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
        "realSensorID": realSensorInstance,
        "sensorKey": "airHumidity",
        "value": 22,
        "timestamp": "2024-04-03 17:04:04",
    }
    ```

    #### Serialized format
    ```
    {
        "realSensorID": realSensorInstance,
        "sensorKey": "airHumidity",
        "value": 22,
    }
    ```
    """

    timestamp = serializers.DateTimeField()  # YYYY-MM-DD hh:mm:ss
    itemName = serializers.CharField(required=False, allow_null=True)
    value = serializers.FloatField()
    realSensor = serializers.PrimaryKeyRelatedField(
        queryset=RealSensorModel.objects.all(),
        required=False,
    )

    class Meta:
        model = SensorModel
        fields = '__all__'

    def create(self, valData):
        """ The method is for the first declaration of the sensor"""
        valData.setdefault("realSensor", None)
        # TODO: add default naming function
        valData.setdefault("itemName", "感測器")
        if valData["realSensor"] is None:
            raise serializers.ValidationError(
                {"realSensor parameter is required when creating Sensor instance"})

        sensor = SensorModel.objects.create(
            sensorKey=valData.pop("sensorKey"),
            realSensor=valData.pop("realSensor"),
            itemName=valData.pop("itemName"),
        )

        valData["sensor"] = sensor
        valData["value"] = valData.pop("value")
        sensorValueSer = SensorValueHistorySerializer()
        sensorValueSer.create(valData)
        return sensor

    def to_representation(self, instance):
        ret = {
            "sensorKey": instance.sensorKey,
            "itemName": instance.itemName,
            "realSensorID": instance.realSensor.realSensorID,
        }
        currentSensorData = list(SensorValueHistoryModel.objects.filter(
            sensor=instance).filter(isCurrent=True))
        if len(currentSensorData) == 0:
            ret["value"] = None
            return ret
        ret["value"] = currentSensorData[0].value

        return ret


class RealSensorSerializer(serializers.ModelSerializer):
    """
    Convert json data to realSensor instance / Convert realSensor instance into dictionary

    #### Json input format for serializer
    ```
    {
        "greenhouse": greenhouseInstance,
        "realSensor": "airSensor", # originally the key of request data
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
                'realSensorID': realSensorInstance,
                'value': 22.0
            },
            {
                'sensorKey': 'airTemp',
                'realSensorID': realSensorInstance,
                'value': 31.0
            }
        ],
    }
    ```
    """

    sensors = SensorSerializer(
        many=True, allow_empty=True, required=False)
    greenhouse = serializers.PrimaryKeyRelatedField(
        queryset=GreenhouseModel.objects.all(),
        required=False,
    )
    itemName = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = RealSensorModel
        fields = '__all__'

    def run_validation(self, data=...):
        data["sensors"] = toList(data.setdefault(
            "sensors", {}), "sensor", "感測項目")
        return super().run_validation(data)

    def __validate(self, validated_data):
        # validate id
        containedID = list(map(lambda x: x.realSensorID, RealSensorModel.objects.filter(
            greenhouse=validated_data["greenhouse"])))
        if validated_data["realSensorID"] in containedID:
            raise serializers.ValidationError(
                {"realSensorID existed in the greenhouse"})

    def update(self, instance, validated_data):
        if validated_data.setdefault("sensors", None):
            raise ValidationError({"can not update sensors data in the API"})

        info = model_meta.get_field_info(instance)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)

        instance.save()

        # Note that many-to-many fields are set after updating instance.
        # Setting m2m fields triggers signals which could potentially change
        # updated instance and we do not want it to collide with .update()
        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)

        return instance

    def create(self, validated_data):
        realSensor = None

        try:
            validated_data.setdefault("itemName", "感測器")  # TODO: add map
            self.__validate(validated_data)
            sensorList: list = validated_data.pop('sensors')
            realSensor = RealSensorModel.objects.create(**validated_data)

            sensorsSerializer = self.fields['sensors']
            for s in sensorList:
                s.setdefault("realSensor", realSensor)
            sensorsSerializer.create(sensorList)
        except Exception as e:
            if realSensor:
                realSensor.delete()
            raise e
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
    controllerSetting = serializers.PrimaryKeyRelatedField(
        queryset=ControllerSettingHistoryModel.objects.all(),
        required=False,
    )

    class Meta:
        model = EvalveScheduleModel
        # generally controllerSetting is also required for creation
        fields = "__all__"

    def create(self, validated_data):
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

    controller = serializers.PrimaryKeyRelatedField(
        queryset=ControllerModel.objects.all(),
        required=False
    )
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
        controllerSetting = None
        try:
            if validated_data.setdefault("controller", None) is None:
                raise serializers.ValidationError(
                    {"controller instance is not provided"})
            self.__pushLastCurrent(validated_data["controller"])

            validated_data.setdefault("openTemp", None)
            validated_data.setdefault("closeTemp", None)
            validated_data.setdefault("evalveSchedules", None)
            validated_data.setdefault("cutHumidity", None)
            evalveSchedulesData = validated_data.pop("evalveSchedules")

            controllerSetting = ControllerSettingHistoryModel.objects.create(
                **validated_data)

            if evalveSchedulesData is not None:
                eSer = self.fields["evalveSchedules"]
                for s in evalveSchedulesData:
                    s["controllerSetting"] = controllerSetting
                eSer.create(evalveSchedulesData)

        except Exception as e:
            if controllerSetting:
                controllerSetting.delete()
            raise e
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
        "controllerID": "evalve_1", # received from the key of request data
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
        "controllerID": "evalve_1", # originally the key of request data
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

    itemName = serializers.CharField(required=False, allow_null=True)
    setting = ControllerSettingSerializer()
    greenhouse = serializers.PrimaryKeyRelatedField(
        queryset=GreenhouseModel.objects.all(),
        many=False,
        required=False,
    )

    class Meta:
        model = ControllerModel
        fields = '__all__'

    def run_validation(self, data=...):
        return super().run_validation(data)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        return attrs

    def __validate(self, validated_data):
        keysMap = {
            "evalve": ["evalveSchedules", "cutHumidity"],
            "shade": ["openTemp", "closeTemp"],
            "fan": ["openTemp", "closeTemp"]
        }
        # validate id
        containedID = list(map(lambda x: x.controllerID, ControllerModel.objects.filter(
            greenhouse=validated_data["greenhouse"])))
        if validated_data["controllerID"] in containedID:
            raise serializers.ValidationError(
                {f"controllerID {validated_data['controllerID']} existed in the greenhouse"})

        if validated_data["controllerKey"] not in keysMap.keys():
            raise serializers.ValidationError({"controllerKey is not defined"})

        for requiredKey in keysMap[validated_data["controllerKey"]]:
            if validated_data["setting"].setdefault(requiredKey, None) is None:
                raise serializers.ValidationError(
                    f"'{requiredKey}' should not be None when 'controllerKey' is '{validated_data['controllerKey']}")

    def create(self, validated_data):
        """
        The method is for the first declaration of the controller. The beginning setting
        would be labled "isCurrent" in controller setting history model. Only the latest
        setting would be labeled with "isCurrent == True" in ControllerSettingHistoryModel
        """
        controller = None
        setting = None
        try:
            validated_data.setdefault(
                "itemName", "default name")  # TODO: add defult naming function
            self.__validate(validated_data)
            settingData = validated_data.pop("setting")

            controller = ControllerModel.objects.create(**validated_data)

            # create new controller
            settingData["controller"] = controller
            controllerSettingSer = self.fields["setting"]
            controllerSettingSer.create(settingData)
        except Exception as e:
            if controller:
                controller.delete()
            raise e

        return controller

    def to_representation(self, instance):
        """
        Get the current controller setting for the controller, serialzie the current controller setting
        to json format. The controller setting might include the following fields
        `["on", "manualControl", "openTemp", "closeTemp", "evalveSchedules]`
        """
        ret = {
            "greenhouseUID": instance.greenhouse.greenhouseUID,
            "controllerID": instance.controllerID,
            "controllerKey": instance.controllerKey,
            "electricity": instance.electricity,
            "itemName": instance.itemName,
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

    ### Json input format for serializer
    ```
    {
            "name": "test_greenhouse",
            "address": "test_address",
            "beginDate": "2011-03-21",
            "realSensors": {
                "AirSensor_1": {
                    "electricity": 100,
                    "lat": 24.112,
                    "lng": 47.330,
                    "sensors": {
                        "airHumidity": {"value": 22, "timestamp": "2024-04-03 17:04:04"},
                        "airTemp": {"value": 31, "timestamp": "2024-04-03 17:04:04"},
                    }
                },
                "AirSensor_2": {
                    "electricity": 100,
                    "lat": 24.112,
                    "lng": 47.330,
                    "sensors": {
                        "airHumidity": {"value": 22, "timestamp": "2024-04-03 17:04:04"},
                        "airTemp": {"value": 31, "timestamp": "2024-04-03 17:04:04"},
                    }
                }
            },
            "controllers": {
                "evalve_1": {
                    "controllerKey": "evalve",
                    "electricity": 100,
                    "lat": 24.112,
                    "lng": 47.330,
                    "setting": {
                        "on": True,
                        "manualControl": False,
                        "evalveSchedules": [
                            {"cutHumidity": 30, "duration": 15,
                                "startTime": "15:00"},
                            {"cutHumidity": 30, "duration": 15,
                                "startTime": "16:00"},
                        ],
                        "timestamp":  "2024-04-03 17:04:04",
                    },

                },
                "Fan_1": {
                    "controllerKey": "fan",
                    "electricity": 100,
                    "lat": 24.112,
                    "lng": 47.330,
                    "setting": {
                        "on": True,
                        "manualControl": False,
                        "openTemp": 21,
                        "closeTemp": 20,
                        "timestamp": "2024-04-03 17:04:04",

                    },
                }
            }
        }
    ```
    """
    """
    # NOTE:
        - JSON: give an owner primary key -> owner instance is given in validated_data
        - Instance: give an owner(user) instance -> user id is given in validated_data (?)
    """
    owner = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=False,
        required=False,
    )
    realSensors = RealSensorSerializer(
        many=True, allow_null=True, allow_empty=True, required=False)
    controllers = ControllerSerializer(
        many=True, allow_null=True, allow_empty=True, required=False)
    greenhouseUID = serializers.UUIDField(required=False)

    class Meta:
        model = GreenhouseModel
        fields = '__all__'

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def run_validation(self, data=...):
        try:
            data["realSensors"] = toList(
                data.setdefault("realSensors", {}), "realSensor", "感測器")
            data["controllers"] = toList(
                data.setdefault("controllers", {}), "controller", "控制器")

        except ValidationError as e:
            raise ValidationError()

        return super().run_validation(data=data)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        return attrs

    def create(self, validated_data):
        greenhouse = None
        try:
            # pop out real_sensors dictionary
            realSensorList: list = validated_data.pop('realSensors')
            # pop out real_controller dictionary
            controllerList: list = validated_data.pop('controllers')

            greenhouse = GreenhouseModel.objects.create(**validated_data)

            # create real sensors
            # TODO: wrap it as a function
            # TODO: use ser.save() method instead
            realSensorsializer = self.fields['realSensors']
            for rS in realSensorList:
                rS.setdefault("greenhouse", greenhouse)
            realSensorsializer.create(realSensorList)

            # create real controllers
            controllersializer = self.fields['controllers']
            for c in controllerList:
                c.setdefault("greenhouse", greenhouse)
            controllersializer.create(controllerList)

        except Exception as e:
            if greenhouse is not None:
                greenhouse.delete()  # the sub items would be deleted as well
            raise e

        return greenhouse

    def to_representation(self, instance: GreenhouseModel):
        ret = super().to_representation(instance)
        return ret


def toList(dataMap: dict, key: str, defaultItemName: str):
    """
    Turn data with following format to list
    #### Map format
    ```
    {
        "XXX_1": {},
        "XXX_2": {},
    }
    ```
    #### List format
    ```
    [
        {
            "xxxID": "XXX_1,
            "itemName": "defaultName",
        },
        {
            "xxxID": "XXX_2",
            "itemName": "defaultName",
        }
    ]
    ```
    """
    ret = []
    ID_SUFFIX = "ID"
    KEY_SUFFIX = "Key"
    ITEM_NAME = "itemName"

    for id, data in dataMap.items():
        data[key+ID_SUFFIX] = id
        data.setdefault(key+KEY_SUFFIX, id.split("_")[0])
        data.setdefault(ITEM_NAME, defaultItemName)
        ret.append(data)
    return ret
