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
a2. implement websocket on getting controller update
"""


class GreenhouseAPI(RealSensorBaseAPI, ControllerBaseAPI):
    """ Initializing all greenhouse objects """

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
            "realSensors": {
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
            },
            "controllers": {
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
                "fan_1": {
                    "greenhouseUID": "oerahjdfjnjn;dbfa",
                    "controllerKey": "fan",
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

        try:
            realSensorDatas = self.parseRealSensorFormat(
                request.data["realSensors"], greenhouseUID=greenhouseUID)

            controllerDatas = self.parseControllerFormat(
                request.data["controllers"], greenhouseUID=greenhouseUID)

            print("realSensor data", realSensorDatas)
            print("controller datas", controllerDatas)

            # validate
            rSensorSer = RealSensorSerializer(data=realSensorDatas, many=True)
            controllerSer = ControllerSerializer(
                data=controllerDatas, many=True)

            if not rSensorSer.is_valid():
                raise ValidationError(rSensorSer.errors)

            if not controllerSer.is_valid():
                raise ValidationError(controllerSer.errors)

            rSensorSer.save()
            controllerSer.save()

            return Response({"message": "item created"}, status=status.HTTP_200_OK)

        except RealSensorModel.DoesNotExist as e:
            print(f"real sensor not found")
            return Response({"error": "real sensor not foound"})

        except GreenhouseModel.DoesNotExist as e:
            print(f"Greenhouse does not exist")
            return Response({"message": "Parent greenhouse not found"}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            print(e.detail)
            return Response({"message": e.detail}, status=status.HTTP_400_BAD_REQUEST)


class RealSensorAPI(RealSensorBaseAPI):

    def post(self, request, greenhouseUID):
        """
        Create real sensor item when the creation request is sent from the sensor. The current value would start to be recoreded at the moment

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
            rSensorDatas = self.parseRealSensorFormat(
                request.data, greenhouseUID=greenhouseUID)
            rSensorSer = RealSensorSerializer(data=rSensorDatas, many=True)

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
        Update the corresponding sensor value from the request object

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

            sensorDatas = []
            for realSensorData in data:
                for sensorKey, sensorValueData in realSensorData["sensors"].items():
                    sensorDatas.append(sensorValueData)

            sensorValueSer = SensorValueHistorySerializer(
                data=sensorDatas, many=True)

            # validate
            if not sensorValueSer.is_valid():
                raise ValidationError(sensorValueSer.errors)

            sensorValueSer.save()

            return Response({"message": "sensor history updated"}, status=status.HTTP_200_OK)

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
            "evalve_3": {
                "greenhouseUID": sample_greenhouse_uid,
                "controllerKey": "evalve",
                "electricity": 100,
                "lat": 24.112,
                "lng": 47.330,
                "setting": {
                    "on": False,
                    "manualControl": False,
                    "timestamp": "2024-04-03 17:04:04",
                    "cutHumidity": 30,
                    "evalveSchedules": [
                           {"duration": 15, "startTime": "15:00"},
                           {"duration": 15, "startTime": "16:00"},
                    ],
                }
            },
            "fan_3": {
                "greenhouseUID": sample_greenhouse_uid,
                "controllerKey": "fan",
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

    def put(self, req, greenhouseUID):
        """
        Update the corresponding controller on/off state

        - method: POST
        - update: update the corresponding data field in database

        #### Request format
        ```
        {
            "evalve_0": {
                "controllerID": "evalve_0", 
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
            "fan_0": {
                "controllerID": "fan_0", 
                "setting": {
                    "on": False,
                    "manualControl": False,
                    "timestamp": "2024-04-03 17:04:04",
                    "openTemp": 21,
                    "closeTemp": 20,
                }
            },
        }

        ```
        """
        try:
            greenhouse = GreenhouseModel.objects.get(
                greenhouseUID=greenhouseUID)

            settingDataList = []
            for controllerID, controllerData in req.data.items():
                controller = ControllerModel.objects.get(
                    greenhouse=greenhouse, controllerID=controllerID)
                controllerData["controller"] = controller.id

                settingDataList.append(controllerData)

            ser = ControllerSettingSerializer(data=settingDataList, many=True)

            if not ser.is_valid():
                print(ser.errors)
                return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

            ser.save()
            return Response({"message": "controller updated"}, status=status.HTTP_200_OK)

        except GreenhouseModel.DoesNotExist:
            print("greenhouse uid:", greenhouseUID)
            return Response({"message": "greenhouse not found"}, status=status.HTTP_404_NOT_FOUND)

        except ControllerModel.DoesNotExist:
            print(f"controllerID {controllerID} not found")
            return Response({"message": f"controllerID {controllerID} not found"}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, greenhouseUID):
        """
        Return the setting of the specified controllers

        - method: POST
        - authentication: "Authorization": "Token <token>"
        - return: the controller setting for an

        ### Return data format
        ```
        {
            "evalve_3": {
                "controllerKey": "evalve",
                "electricity": 100,
                "lat": 24.112,
                "lng": 47.330,
                "setting": {
                    "on": False,
                    "manualControl": False,
                    "timestamp": "2024-04-03 17:04:04",
                    "cutHumidity": 30,
                    "evalveSchedules": [
                           {"duration": 15, "startTime": "15:00"},
                           {"duration": 15, "startTime": "16:00"},
                    ],
                }
            },
            "fan_3": {
                "controllerKey": "fan",
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

        try:
            greenhouse = GreenhouseModel.objects.get(
                greenhouseUID=greenhouseUID)

            allControllers = list(ControllerModel.objects.filter(
                greenhouse=greenhouse
            ))

            controllerData = self.parseToControllerFormat(allControllers)

            return Response(controllerData, status=status.HTTP_200_OK)

        except GreenhouseModel.DoesNotExist:
            print("Greenhouse not found")
            return Response({"message": "Parent greenhouse not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            print(e)
            return Response({"message": "server error occurs"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
