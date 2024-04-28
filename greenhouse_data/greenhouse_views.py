from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from datetime import datetime

from .models import *
from .serializer import *


class CreateRealSensorAPI(APIView):
    """
    Create real sensor item when the creattion request is sent from the sensor. The current value would start to be recoreded at the moment

    - method: POST
    - authentication: "Authorization": "Token <token>"
    #### Return format example
    {
        "message": "item created",
        "realSensorUID": "123456",
    }

    #### Post format example
    {
        "greenhouseUID": "0a94ejoidjrsdvj",
        "realSensors": {
            "AIR_SENSOR_1": {
                "electricity": 100,
                "lat": 24.112,
                "lng": 47.330,
                "sensors": {
                    "airHumidity": {"value": 22, "timestamp": "2024-04-03 17:04:04"},
                    "airTemp": {"value": 31, "timestamp": "2024-04-03 17:04:04"},
                }
            },
            "AIR_SENSOR_2": {
                "electricity": 100,
                "lat": 24.112,
                "lng": 47.330,
                "sensors": {
                    "airHumidity": {"value": 22, "timestamp": "2024-04-03 17:04:04"},
                    "airTemp": {"value": 31, "timestamp": "2024-04-03 17:04:04"},
                }
            }
        },
    }

    """

    def post(self, request):
        # NOTE: we can try using PrimaryKeyField for greenhouse in serializer, so we only has to input greenhouseUID instead of an instance
        greenhouse = GreenhouseModel.objects.get(
            uid=request.data.pop("greenhouseUID"))

        rSensors: dict = request.data["realSensors"]
        for realSensorID, rSensorData in rSensors.items():
            rSensorData["greenhouse"] = greenhouse
            rSensorData["realSensorID"] = realSensorID
            rSensorSer = RealSensorSerializer()
            rSensorSer.create(rSensorData)

        result = {
            "message": "item created",
        }
        return Response(result, status=status.HTTP_200_OK)


class CreateControllerAPI(APIView):
    """
    Create controller when the creation request is sent from the controller

    - method: POST
    - authentication: "Authorization": "Token <token>"
    #### Return format example
    {
        "message": "item created",
        "realControllerID": "123456",
    }

    #### Post format example
    {
        "greenhouseUID": "1221adfadslj",
        "controllers": {
            "Watering_1": {
                "controllerKey": "evalve",
                "electricity": 100,
                "lat": 24.112,
                "lng": 47.330,
                "setting": {
                    "on": False,
                    "manualControl": False,
                    "timestamp": "2024-04-03 17:04:04",
                    "evalveSchedules": [
                        {"cutHumidity": 30, "duration": 15, "startTime": "15:00"},
                        {"cutHumidity": 30, "duration": 15, "startTime": "16:00"},
                    ],
                }
            },
            "Fan_1": {
                "controllerKey": "evalve",
                "electricity": 100,
                "lat": 24.112,
                "lng": 47.330,
                "setting": {
                    "on": False,
                    "manualControl": False,
                    "timestamp": "2024-04-03 17:04:04",
                    "openTemp": 21,
                    "closeTemp": 20,
                }

            }
        }
    }
    """

    def post(self, request):
        # NOTE: we can try using PrimaryKeyField for greenhouse in serializer, so we only has to input greenhouseUID instead of an instance
        greenhouse = GreenhouseModel.objects.get(
            uid=request.data.pop("greenhouseUID"))

        contrllersDatas: dict = request.data["controllers"]
        for controllerID, controllerData in contrllersDatas.items():
            controllerData["greenhouse"] = greenhouse
            controllerData["controllerID"] = controllerID
            controllerSer = ControllerSerializer()
            controllerSer.create(controllerData)

        result = {
            "message": "item created",
        }
        return Response(result, status=status.HTTP_200_OK)


class GetControllerSetting(APIView):
    """
    Return the setting of the specified controllers

    - method: POST
    - authentication: "Authorization": "Token <token>"
    - return: the controller setting for an

    #### Post datas format
    ```
    {
        "greenhouseUID": "340we9ufijsn",
        "controllerID": ["WATERING_0", "FAN_1"],
    }
    ```

    ### Return data format
    ```
    {
        "WATERING_0": {
            "openTemp": 31.2, # ignored if not used
            "closeTemp": 30.1, # ignored if not used
            "evalveSchedules": [ # ignored if not used
                {"cutHumidity": 24.1, "duration": 15, "startTime": "15:00"},
                {"cutHumidity": 24.3, "duration": 15, "startTime": "12:00"}
            ]
        },
        "FAN_1": {
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

    def post(self, request):
        greenhouse = GreenhouseModel.objects.get(
            uid=request.data["greenhouseUID"])

        # validate
        if request.data["greenhouseUID"] is None:
            print("greenhouseUID is not included in request data")
            return Response({"please include greenhouseUID in request data"}, status=status.HTTP_400_BAD_REQUEST)
        if request.data["controllerID"] is None:
            print("controllerID is not included in request data")
            return Response("please include controllerID in request data", status=status.HTTP_400_BAD_REQUEST)

        ret = {}
        for controllerID in request.data["controllerID"]:

            controller = list(ControllerModel.objects.filter(
                greenhouse=greenhouse, controllerID=controllerID))

            if len(controller) == 0:
                print("warning: request for non-exist controller")
                continue

            controllerSer = ControllerSerializer(controller[0])
            ret[controllerID] = controllerSer.data["setting"]
        return Response(ret, status=status.HTTP_200_OK)


class GetAllControllerSetting(APIView):
    """
    (for greenhouse) This class provide method to receive the setting data
    for all controllers in a greenhouse

    - method: POST
    - authentication: "Authorization": "Token <token>"
    - return: the controller setting for an

    #### Post datas format
    ```
    {
        "greenhouseUID": "340we9ufijsn",
    }
    ```

    ### Return data format
    ```
    {
        "WATERING_0": {
            "openTemp": 31.2, # ignored if not used
            "closeTemp": 30.1, # ignored if not used
            "evalveSchedules": [ # ignored if not used
                {"cutHumidity": 24.1, "duration": 15, "startTime": "15:00"},
                {"cutHumidity": 24.3, "duration": 15, "startTime": "12:00"}
            ]
        },
        "FAN_1": {
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

    def post(self, request):
        greenhouse = GreenhouseModel.objects.get(
            uid=request.data["greenhouseUID"])

        # validate
        if request.data["greenhouseUID"] is None:
            print("greenhouseUID is not included in request data")
            return Response({"please include greenhouseUID in request data"}, status=status.HTTP_400_BAD_REQUEST)

        ret = {}
        controllers = list(
            ControllerModel.objects.filter(greenhouse=greenhouse))
        for controller in controllers:
            controllerSer = ControllerSerializer(controller)
            controllerID = controllerSer.data["controllerID"]
            controllerSer.data.setdefault("setting", None)
            ret[controllerID] = controllerSer.data["setting"]
        return Response(ret, status=status.HTTP_200_OK)


class UpdateRealSensorDataAPI(APIView):
    """
    Update the corresponding sensor data from the request object

    - method: POST
    - update: update the corresponding data field in database

    #### Request format
    ```
    {
        "greenhouseUID": "a9jwjenfaksj",
        "realSensors": {
            "AIR_SENSOR_1": {
                "airHumidity": {"value": 22, "timestamp": "2024-04-03 17:04:04"},
                "airTemp": {"value": 31, "timestamp": "2024-04-03 17:04:04"},
            },
            "AIR_SENSOR_2": {
                "airHumidity": {"value": 22, "timestamp": "2024-04-03 17:04:04"},
                "airTemp": {"value": 31, "timestamp": "2024-04-03 17:04:04"},
            }
        },
    }
    ```
    """

    def post(self, request):
        greenhouse = GreenhouseModel.objects.get(
            uid=request.data["greenhouseUID"])

        notFound = []
        for realSensorID, realSensorData in request.data["realSensors"].items():
            realSensor = list(RealSensorModel.objects.filter(
                greenhouse=greenhouse, realSensorID=realSensorID))

            if len(realSensor) == 0:
                print("real sensor not found")
                notFound.append(realSensorID)
                continue

            for sensorKey, sensorValueData in realSensorData.items():

                sensor = SensorModel.objects.get(
                    parentItem=realSensor[0], sensorKey=sensorKey)

                sensorValueData["sensor"] = sensor
                sensorValueSer = SensorValueHistorySerializer()
                sensorValueSer.create(sensorValueData)

        return Response({"message": "sensor history updated", "notFound": notFound}, status=status.HTTP_200_OK)
