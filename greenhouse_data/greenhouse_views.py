from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from datetime import datetime

from .models import *
from .serializer import *
from .api_base import *

"""
TODO:
1. use parent class to separate app and greenhouse api
2. use url parameter for every api for getting information
"""


class RealSensorAPI(RealSensorBaseAPI):

    def post(self, request, greenhouseUID):
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
            "AirSensor_1": {
                "greenhouseUID": "1234",
                "realSensorID": "AirSensor",
                "electricity": 4.12,
                "address":
                {
                    "lat": 24.112,
                    "lng": 47.330
                },
                "sensors":
                {
                    "airTemp": 33,
                    "airHumidity": 68,
                    "timeStamp": "2024-04-18 17:04:04"
                }
            },
        }

        """

        try:
            data = self.parseRealSensorFormat(
                request.data, greenhouseUID=greenhouseUID)
            for realSensorID, rSensorData in data.items():
                rSensorSer = RealSensorSerializer(data=rSensorData)

                if not rSensorSer.is_valid():
                    raise ValidationError(rSensorSer.errors)

                rSensorSer.save()

            return Response({"message": "item created"}, status=status.HTTP_200_OK)

        except RealSensorModel.DoesNotExist as e:
            print(f"real sensor not found")
            return Response({"error": "real sensor not foound"})

        except GreenhouseModel.DoesNotExist as e:
            print(f"Greenhouse does not exist")
            return Response({"message": "Parent greenhouse not found"}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            print(e)
            return Response({"message": e.detail}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, greenhouseUID):
        """
        Update the corresponding sensor data from the request object

        - method: POST
        - update: update the corresponding data field in database

        #### Request format
        ```
        {
            "AirSensor_1": {
                "greenhouseUID": "1234",
                "realSensorID": "AirSensor",
                "electricity": 4.12,
                "address":
                {
                    "lat": 24.112,
                    "lng": 47.330
                },
                "sensors":
                {
                    "airTemp": 33,
                    "airHumidity": 68,
                    "timeStamp": "2024-04-18 17:04:04"
                }
            },
        }
        ```
        """
        try:
            data = self.parseRealSensorFormat(
                request.data, greenhouseUID=greenhouseUID)

            notFound = []
            for realSensorID, realSensorData in data.items():
                for sensorKey, sensorValueData in realSensorData["sensors"].items():
                    sensorValueSer = SensorValueHistorySerializer(
                        data=sensorValueData)

                    # validate
                    if not sensorValueSer.is_valid():
                        raise ValidationError(sensorValueSer.errors)

                    sensorValueSer.save()

            return Response({"message": "sensor history updated", "notFound": notFound}, status=status.HTTP_200_OK)

        except RealSensorModel.DoesNotExist as e:
            print(f"real sensor not found", e)
            return Response({"message": "real sensor not found"}, status=status.HTTP_404_NOT_FOUND)

        except GreenhouseModel.DoesNotExist as e:
            print(f"Greenhouse does not exist")
            return Response({"message": "Parent greenhouse not found"}, status=status.HTTP_404_NOT_FOUND)

        except ValidationError as e:
            print(e)
            return Response({"message": e.detail}, status=status.HTTP_400_BAD_REQUEST)


class ControllerAPI(ControllerBaseAPI):
    def post(self, request, greenhouseUID):
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
        ```
        {
            "evalve_1": {
                "greenhouseUID": "aeprjsdlknafln",
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
                "greenhouseUID": "oerahjdfjnjn;dbfa",
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
        ```
        """
        # NOTE: we can try using PrimaryKeyField for greenhouse in serializer, so we only has to input greenhouseUID instead of an instance
        try:
            data = self.parseControllerFormat(
                request.data, greenhouseUID=greenhouseUID)
            for controllerData in data.values():
                controllerSer = ControllerSerializer(data=controllerData)

                if not controllerSer.is_valid():
                    raise ValidationError(detail=controllerSer.errors)

                controllerSer.save()

            return Response({"message": "item created"}, status=status.HTTP_200_OK)

        except GreenhouseModel.DoesNotExist as e:
            print(f"Greenhouse does not exist")
            return Response({"message": "Parent greenhouse not found"}, status=status.HTTP_404_NOT_FOUND)

        except ValidationError as e:
            print(e)
            return Response({"message": e.detail}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, greenhouseUID):
        """
        Return the setting of the specified controllers

        - method: POST
        - authentication: "Authorization": "Token <token>"
        - return: the controller setting for an

        ### Return data format
        ```
        {
            "evalve_0": {
                "openTemp": 31.2, # ignored if not used
                "closeTemp": 30.1, # ignored if not used
                "evalveSchedules": [ # ignored if not used
                    {"cutHumidity": 24.1, "duration": 15, "startTime": "15:00"},
                    {"cutHumidity": 24.3, "duration": 15, "startTime": "12:00"}
                ]
            },
            "fan_1": {
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

        try:
            greenhouse = GreenhouseModel.objects.get(
                greenhouseUID=greenhouseUID)

            allControllers = list(ControllerModel.objects.filter(
                greenhouse=greenhouse
            ))

            controllerData = {}
            for controller in allControllers:
                controllerSer = ControllerSerializer(controller)
                controllerData[controllerSer.data["controllerID"]
                               ] = controllerSer.data["setting"]

            return Response(controllerData, status=status.HTTP_200_OK)

        except GreenhouseModel.DoesNotExist:
            print("Greenhouse not found")
            return Response({"message": "Parent greenhouse not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            print(e)
            return Response({"message": "server error occurs"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
