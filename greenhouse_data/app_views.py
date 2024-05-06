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

# TODO: implement all apis


class Greenhouse(GetGreenhouseBase):
    """
    API to create greenhouse or get all greenhouses for the user
    """

    # create
    def post(self, request):
        """
        Enable administrators to easily create a new greenhouse. No sensors and controller data are sent when greenhosue is created by admin user.

        - method: POST
        - paramters: greenhouse data map
        - server: update greenhouse dataset for the user
        - return: greenhouse uid (in the same order)

        #### Post format example
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

        #### Return format
        ```
        {
            "message": "greenhouse created,
            "greenhouseUID": "sdoi3u4eoijsdx;fae",
        }
        """
        try:
            user_id = request.user.id

            payload = request.data
            payload["owner"] = user_id

            ser = GreenhouseSerializer(data=payload)
            if ser.is_valid():
                greenhouse_instance = ser.save()
                result = {
                    "message": "greenhouse created",
                    "greenhouseUID": greenhouse_instance.greenhouseUID,
                }
                return Response(result, status=status.HTTP_201_CREATED)

            print("validation error:", ser.errors)
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            raise e

    # get all api
    def get(self, request):
        """
        #### Return data format
        {
            "greenhouseUID": "cf7cf83d-2983-4c49-b22c-5ff98cd99d88",
            "owner": 1,
            "name": "test_greenhouse",
            "address": "test_address",
            "beginDate": "2011-03-21",
            "photo": null,
            "realSensors": [
                {
                    "id": 12,
                    "greenhouse": "cf7cf83d-2983-4c49-b22c-5ff98cd99d88",
                    "itemName": "感測器",
                    "realSensorID": "AirSensor_1",
                    "realSensorKey": "AirSensor",
                    "electricity": 100.0,
                    "lat": 24.112,
                    "lng": 47.33
                },
                {
                    "id": 13,
                    "greenhouse": "cf7cf83d-2983-4c49-b22c-5ff98cd99d88",
                    "itemName": "感測器",
                    "realSensorID": "AirSensor_2",
                    "realSensorKey": "AirSensor",
                    "electricity": 100.0,
                    "lat": 24.112,
                    "lng": 47.33
                }
            ],
            "sensors": {
            "airHumidity": [
                {
                    "itemName": "感測項目",
                    "realSensorID": 12,
                    "value": 22.0
                },
                {
                    "itemName": "感測項目",
                    "realSensorID": 13,
                    "value": 22.0
                }
            ],
            "airTemp": [
                {
                "itemName": "感測項目",
                "realSensorID": 12,
                "value": 31.0
                },
                {
                "itemName": "感測項目",
                "realSensorID": 13,
                "value": 31.0
                }
            ]
            },
            "controllers": {
            "fan": [
                {
                    "greenhouseUID": "cf7cf83d-2983-4c49-b22c-5ff98cd99d88",
                    "controllerID": "Fan_1",
                    "controllerKey": "fan",
                    "electricity": 100.0,
                    "itemName": "控制器",
                    "lat": 24.112,
                    "lng": 47.33,
                    "setting": {
                        "id": 15,
                        "controller": 16,
                        "openTemp": 21.0,
                        "closeTemp": 20.0,
                        "evalveSchedules": [],
                        "timestamp": "2024-04-03T17:04:04Z",
                        "isCurrent": true
                    },
                    "on": true,
                    "manualControl": false
                }
            ],
            "evalve": [
                {
                    "greenhouseUID": "cf7cf83d-2983-4c49-b22c-5ff98cd99d88",
                    "controllerID": "evalve_1",
                    "controllerKey": "evalve",
                    "electricity": 100.0,
                    "itemName": "控制器",
                    "lat": 24.112,
                    "lng": 47.33,
                    "setting": {
                        "id": 14,
                        "controller": 15,
                        "openTemp": null,
                        "closeTemp": null,
                        "timestamp": "2024-04-03T17:04:04Z",
                        "isCurrent": true,
                        "cutHumidity": [
                        30.0,
                        30.0
                        ],
                        "duration": [
                        "00:00:15",
                        "00:00:15"
                        ],
                        "startTime": [
                        "15:00:00",
                        "16:00:00"
                        ]
                    },
                    "on": true,
                    "manualControl": false
                }
            ]
            }
        }
        """
        user = request.user  # instance ?
        greenhouses = list(GreenhouseModel.objects.filter(owner=user))

        resultList = []

        for g in greenhouses:
            gSer = GreenhouseSerializer(g)
            retData = self.parseToAppFormat(gSer.data)
            resultList.append(retData)

        return Response(
            resultList,
            status=status.HTTP_200_OK
        )


class GreenhouseDetail(GetGreenhouseBase):
    """
    API to get, update, or delete a greenhouse
    # UNDONE: need api for updating greenhouse
    """

    def delete(self, request, greenhouseUID):
        """
        Delete the greenhouse with uid == greenhouseUID

        - method: DELETE
        - authentication: "Authorization"" "Token <token>"
        """

        GreenhouseModel.objects.get(uid=greenhouseUID).delete()
        return Response({"message": "greenhouse is deleted"}, status=status.HTTP_200_OK)

    def get(self, req, greenhouseUID):
        try:
            greenhouse = GreenhouseModel.objects.get(
                greenhouseUID=greenhouseUID)
        except GreenhouseModel.DoesNotExist:
            return Response({"error": "greenhouse does not exist"}, status=status.HTTP_404_NOT_FOUND)

        ser = GreenhouseSerializer(greenhouse)
        greenhouseData = self.parseToAppFormat(ser.data)
        return Response(greenhouseData, status=status.HTTP_200_OK)


class Controller(AppBaseAPI):
    """
    API to get all controllers in a greenhouse
    """

    def get(self, request, greenhouseUID):
        """ Get all controller in the greenhouse"""
        try:
            greenhouse = GreenhouseModel.objects.get(
                greenhouseUID=greenhouseUID)

            ret = {}
            controllers = list(
                ControllerModel.objects.filter(greenhouse=greenhouse))

            for controller in controllers:
                controllerSer = ControllerSerializer(controller)
                controllerID = controllerSer.data["controllerID"]
                ret[controllerID] = controllerSer.data["setting"]

            return Response(ret, status=status.HTTP_200_OK)

        except GreenhouseModel.DoesNotExist:
            print("greenhouse does not exist")
            return Response({"error": "greenhouse does not exist"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, req, greenhouseUID):
        """
        Update the corresponding controller setting

        - method: POST
        - update: update the corresponding data field in database

        #### Request format
        ```
        [
            {
                "controllerID": "evalve_0", 
                "setting": {
                    "on": True,
                    "manualControl": False,
                    "timestamp": "2024-04-03 17:04:04",
                    "cutHumidity": 21.3,
                    "evalveSchedules": [
                        {"duration": 12, "startTime": "15:00"},
                    ]
                }
            },
            {
                "controllerID": "evalve_1", 
                "setting": {
                    "on": True,
                    "manualControl": False,
                    "timestamp": "2024-04-03 17:04:04",
                    "cutHumidity": 21.3,
                    "evalveSchedules": [
                        {"duration": 12, "startTime": "15:00"},
                    ]
                }
            },
        ]

        ```
        """
        try:
            greenhouse = GreenhouseModel.objects.get(
                greenhouseUID=greenhouseUID)

            for controllerData in req.data:
                controller = ControllerModel.objects.get(
                    greenhouse=greenhouse, controllerID=controllerData["controllerID"])
                settingData = controllerData["setting"]
                settingData["controller"] = controller.id
                ser = ControllerSettingSerializer(data=settingData)

                if not ser.is_valid():
                    print(ser.errors)
                    return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

                ser.save()
            return Response({"message": "controller updated"}, status=status.HTTP_200_OK)

        except GreenhouseModel.DoesNotExist:
            print("greenhouse uid:", greenhouseUID)
            return Response({"message": "greenhouse not found"}, status=status.HTTP_404_NOT_FOUND)

        except ControllerModel.DoesNotExist:
            print(f"controllerID {controllerData['controllerID']} not found")
            return Response({"message": f"controllerID {controllerData['controllerID']} not found"}, status=status.HTTP_404_NOT_FOUND)


class ControllerDetail(AppBaseAPI):
    """ API to update, delete or get a specific controller"""

    def patch(self, request, greenhouseUID, controllerID):
        """
        Update the basic info of a controller # NOTE: there is nothing to be changed currently

        - method: PATCH
        - authentication: "Authorization": "Token <token>"
        - return: new controller configuration

        #### Request format
        ```
        {
            "greenhouseUID": "a9jwjenfaksj",
            "controllerID": "evalve_1",
            # fields to be changed
            "lat": 32.1, # optional
            "lng": 18.3, # optional
        }
        ```
        """
        payload = request.data

        try:
            greenhouse = GreenhouseModel.objects.get(
                greenhouseUID=greenhouseUID)
            controller = ControllerModel.objects.get(
                greenhouse=greenhouse, controllerID=controllerID)

            # update
            ser = ControllerSerializer(
                controller, data=payload, partial=True)

            if ser.is_valid():
                ser.save()
                ret = ser.data
                ret["greenhouseUID"] = ser.data["greenhouseUID"]
                return Response(ret, status=status.HTTP_200_OK)

            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        except GreenhouseModel.DoesNotExist:
            print(f"greenhouse {greenhouseUID} not found")
            return Response({"message": "greenhouse not found"}, status=status.HTTP_404_NOT_FOUND)
        except ControllerModel.DoesNotExist:
            print(f"controllerID {controllerID} not found")
            return Response({"message": f"controllerID {controllerID} not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, greenhouseUID, controllerID):
        payload = request.data

        try:
            greenhouse = GreenhouseModel.objects.get(
                greenhouseUID=greenhouseUID)
            controller = ControllerModel.objects.get(
                greenhouse=greenhouse, controllerID=controllerID)
        except GreenhouseModel.DoesNotExist:
            print(f"greenhouse {greenhouseUID} not found")
            return Response({"message": "greenhouse not found"}, status=status.HTTP_404_NOT_FOUND)
        except ControllerModel.DoesNotExist:
            print(f"controllerID {controllerID} not found")
            return Response({"message": f"controllerID {controllerID} not found"}, status=status.HTTP_404_NOT_FOUND)

        controller.delete()
        return Response({"message": "realSensor is deleted"}, status=status.HTTP_200_OK)


class RealSensorAPI(AppBaseAPI):
    """ API for deleting, updating and getting real sensor detail"""

    def patch(self, request, greenhouseUID, realSensorID):
        """ Update real sensor basic information """
        payload = request.data

        # get data
        try:
            greenhouse = GreenhouseModel.objects.get(
                greenhouseUID=greenhouseUID)
            realSensor = RealSensorModel.objects.get(
                greenhouse=greenhouse, realSensorID=realSensorID)

            # update
            ser = RealSensorSerializer(
                realSensor, data=payload, partial=True)

            if ser.is_valid():
                ser.save()
                return Response({"message": "sensor updated"}, status=status.HTTP_200_OK)
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        except GreenhouseModel.DoesNotExist:
            print(f"greenhouse {greenhouseUID} not found")
            return Response({"message": "greenhouse not found"}, status=status.HTTP_404_NOT_FOUND)
        except ControllerModel.DoesNotExist:
            print(f"realSensorID: {realSensorID} no found")
            return Response({"errors": f"realSensorID: {realSensorID} no found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, greenhouseUID, realSensorID):
        payload = request.data

        try:
            greenhouse = GreenhouseModel.objects.get(
                greenhouseUID=greenhouseUID)
            realSensor = RealSensorModel.objects.get(
                greenhouse=greenhouse, realSensorID=realSensorID)

            realSensor.delete()

            return Response("realSensor is deleted", status=status.HTTP_200_OK)

        except GreenhouseModel.DoesNotExist:
            print(f"greenhouse {greenhouseUID} not found")
            return Response({"message": "greenhouse not found"}, status=status.HTTP_404_NOT_FOUND)
        except ControllerModel.DoesNotExist:
            print(f"realSensorID: {realSensorID} no found")
            return Response({"errors": f"realSensorID: {realSensorID} no found"}, status=status.HTTP_404_NOT_FOUND)


class SensorAPI(AppBaseAPI):

    # UNDONE: not fully implemented
    def get(self, request):
        """
        Return the history data information of a sensor in specific time range.

        - method: POST
        - authentication: "Authorization": "Token <token>"
        - return: list of history values, start date, unitScale, datelength

        #### Post datas format
        """
        raise NotImplementedError
