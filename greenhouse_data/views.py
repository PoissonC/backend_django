from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from datetime import datetime

from .models import *
from .serializer import *

# TODO: implement all apis


"""
Creation API
"""


class CreatGreenhouseAPI(APIView):
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
            "AIR_SENSOR_1": {
                "type": "airSensor",
                "electricity": 100,
                "lat": 24.112,
                "lng": 47.330,
                "sensors": {
                    "airHumidity": {"value": 22, "timestamp": "2024-04-03 17:04:04"},
                    "airTemp": {"value": 31, "timestamp": "2024-04-03 17:04:04"},
                }
            }
            "AIR_SENSOR_2": {
                "type": "airSensor",
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
            "Watering_1": {
                "controllerKey": "evalve",
                "electricity": 100,
                "lat": 24.112,
                "lng": 47.330,
                "evalveSchedules": [
                    {"cutHumidity": 30, "duration": 15, "startTime": "15:00"},
                    {"cutHumidity": 30, "duration": 15, "startTime": "16:00"},
                ],
            }
            "Fan_1": {
                "controllerKey": "evalve",
                "electricity": 100,
                "lat": 24.112,
                "lng": 47.330,
                "openTemp": 21,
                "closeTemp": 20,
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
    ```
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.user.id

        payload = request.data
        payload["owner"] = user_id

        # TODO: remove these lines to enable deep initialization
        payload["realSensors"] = []
        payload["controllers"] = []

        ser = GreenhouseSerializer(data=payload)

        if ser.is_valid():
            ser.save()
            result = {
                "message": "greenhouse created",
                "greenhouseUID": ser.instance.uid,
            }
            return Response(result, status=status.HTTP_201_CREATED)

        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


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
    permission_classes = [IsAuthenticated]

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


"""
Delete API
"""


class DeleteGreenhouseAPI(APIView):
    """
    Delete the greenhouse with uid == greenhouseUID

    - method: DELETE
    - authentication: "Authorization"" "Token <token>"

    #### Request data format
    ```
    {
        "greenhouseUID": "1dasdfhjsdf832"
    }
    ```
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        payload = request.data
        payload.setdefault("greenhouseUID", None)

        # validate
        if payload["greenhouseUID"] is None:
            print("greenhouseUID is not included in request data")
            return Response({"please include greenhouseUID in request data"}, status=status.HTTP_400_BAD_REQUEST)

        GreenhouseModel.objects.get(uid=payload["greenhouseUID"]).delete()
        return Response({"greenhouse is deleted"}, status=status.HTTP_200_OK)


class DeleteRealSensorAPI(APIView):
    """
    Delete the real sensor data

    - method: DELETE
    - authentication: "Authorization"" "Token <token>"

    #### Request data format
    ```
    {
        "greenhouseUID": "awep09uifojd",
        "realSensorID": "1",
    }
    ```
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        payload = request.data
        payload.setdefault("greenhouseUID", None)
        payload.setdefault("realSensorID", None)

        # validate
        if payload["greenhouseUID"] is None:
            print("greenhouseUID is not included in request data")
            return Response({"please include greenhouseUID in request data"}, status=status.HTTP_400_BAD_REQUEST)
        if payload["realSensorID"] is None:
            print("realSensorID is not included in request data")
            return Response("please include realSensorID in request data", status=status.HTTP_400_BAD_REQUEST)

        try:
            greenhouse = GreenhouseModel.objects.get(
                uid=payload["greenhouseUID"])
            realSensor = RealSensorModel.objects.get(
                greenhouse=greenhouse, realSensorID=payload["realSensorID"])
        except Exception as e:
            print(e)
            return Response("content not found", status=status.HTTP_204_NO_CONTENT)

        realSensor.delete()

        return Response("realSensor is deleted", status=status.HTTP_200_OK)


class DeleteControllerAPI(APIView):
    """
    Delete the real sensor data

    - method: DELETE
    - authentication: "Authorization"" "Token <token>"

    #### Request data format
    ```
    {
        "greenhouseUID": "awep09uifojd",
        "controllerID": "1",
    }
    ```
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        payload = request.data
        payload.setdefault("greenhouseUID", None)
        payload.setdefault("controllerID", None)

        # validate
        if payload["greenhouseUID"] is None:
            print("greenhouseUID is not included in request data")
            return Response({"please include greenhouseUID in request data"}, status=status.HTTP_400_BAD_REQUEST)
        if payload["controllerID"] is None:
            print("controllerID is not included in request data")
            return Response("please include controllerID in request data", status=status.HTTP_400_BAD_REQUEST)

        try:
            greenhouse = GreenhouseModel.objects.get(
                uid=payload["greenhouseUID"])
            controller = ControllerModel.objects.get(
                greenhouse=greenhouse, controllerID=payload["controllerID"])
        except Exception as e:
            print(e)
            return Response("content not found", status=status.HTTP_204_NO_CONTENT)

        controller.delete()
        return Response("realSensor is deleted", status=status.HTTP_200_OK)


"""
Get API
"""


class GetGreenhouseBasicInfoAPI(APIView):
    """
    Return the uids and basic infos for all the greenhouses belong to the user

    - method: GET
    - authentication: "Authorization"" "Token <token>"
    - return: list of greenhouse uids
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user
        greenhouses = list(GreenhouseModel.objects.filter(owner=user))

        resultList = []

        for g in greenhouses:
            resultList.append(
                {
                    "uid": g.uid,
                    "name": g.name,
                    "address": g.address,
                    "beginDate": g.beginDate,
                }
            )

        return Response(
            resultList,
            status=status.HTTP_200_OK
        )


class GetGreenhouseDataAPI(APIView):
    """
    Return a list of greenhouseMainData map for the user

    - method: GET
    - authentication: "Authorization": "Token <token>"
    - return: list of greenhouseMainData
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user  # instance ?
        greenhouses = list(GreenhouseModel.objects.filter(owner=user))

        resultList = []

        for g in greenhouses:
            gSer = GreenhouseSerializer(g)
            resultList.append(gSer.data)

        return Response(
            resultList,
            status=status.HTTP_200_OK
        )


class GetControllerSettingToGre(APIView):
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


class GetAllControllerSettingToGre(APIView):
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
            controller.data.setdefault("setting", None)
            ret[controllerID] = controllerSer.data["setting"]
        return Response(ret, status=status.HTTP_200_OK)


class GetControllerSettingToApp(APIView):
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
    permission_classes = [IsAuthenticated]

    def post(self, request):
        greenhouse = GreenhouseModel.objects.get(uid=request.data["uid"])

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
            ret[controllerID] = controllerSer.data["setting"]
        return Response(ret, status=status.HTTP_200_OK)


class GetSensorCurrentDataToApp(APIView):
    """
    Return the current value of the specified controllers

    - method: POST
    - authentication: "Authorization": "Token <token>"
    - return: the controller setting for an

    #### Post datas format
    ```
    {
        "greenhouseUID": "340we9ufijsn",
        "sensorKeys": [
            "airHumidity",
            "soidCO2",
        ],
    }
    ```

    #### Return data format
    ```
    {
        "airHumidity": [
            {
                "realSensorID": "AirSensor1",
                "realSensorName": "AirSensor1",
                "sensorKey": "airHumidity",
                "currentValue": 31.1,
            },
            {
                "realSensorID": "AirSensor2",
                "realSensorName": "AirSensor2",
                "sensorKey": "airHumidity",
                "currentValue": 31.1,
            },
        ],

        "soidCO2": [
            {
                "realSensorID": "SoidSensor1",
                "realSensorName": "SoidSensor1",
                "sensorKey": "soidCO2",
                "currentValue": 31.1,
            },
            {
                "realSensorID": "SoidSensor2",
                "realSensorName": "SoidSensor2",
                "sensorKey": "soidCO2",
                "currentValue": 31.1,
            },
        ]
    }

    ```
    """
    permission_classes = [IsAuthenticated]

    def parseID(self, id: str):
        pass

    def post(self, request):
        # validate
        request.data.setdefault("greenhouseUID", None)
        request.data.setdefault("sensorKeys", None)

        if request.data["greenhouseUID"] is None:
            print("greenhouseUID is not included in request data")
            return Response({"please include greenhouseUID in request data"}, status=status.HTTP_400_BAD_REQUEST)
        if request.data["sensorKeys"] is None:
            print("sensorKeys is not included in request data")
            return Response({"please include sensorKeys in request data"}, status=status.HTTP_400_BAD_REQUEST)

        greenhouse = GreenhouseModel.objects.get(
            uid=request.data["greenhouseUID"])

        realSensors = list(
            RealSensorModel.objects.filter(greenhouse=greenhouse))

        if len(realSensors) == 0:
            return Response({"message": "no sensor found"}, status=status.HTTP_204_NO_CONTENT)

        allSensors = SensorModel.objects.filter(parentItem__in=realSensors)

        if len(allSensors) == 0:
            return Response({"message": "no sensor found"}, status=status.HTTP_204_NO_CONTENT)

        ret = {}
        for sensorKey in request.data["sensorKeys"]:
            ret[sensorKey] = []
            selectedSensors = list(allSensors.filter(sensorKey=sensorKey))

            for sensor in selectedSensors:
                sensorData = SensorSerializer(sensor).data
                sensorData["realSensorID"] = sensorData.pop(
                    "parentItem").realSensorID
                ret[sensorKey].append(sensorData)

        return Response(ret, status=status.HTTP_200_OK)


class GetSensorHistoryAPI(APIView):

    # UNDONE: not fully implemented
    def post(self, request):
        """
        Return the history data information of a sensor in specific time range.

        - method: POST
        - authentication: "Authorization": "Token <token>"
        - return: list of history values, start date, unitScale, datelength

        #### Post datas format
        """
        raise NotImplementedError


"""
Update API
"""


class UpdateControllerInfoAPI(APIView):
    def patch(self, request):
        """
        Update the basic info of a controller # NOTE: there is nothing to be changed currently

        - method: PATCH
        - authentication: "Authorization": "Token <token>"
        - return: new controller configuration

        #### Request format
        ```
        {
            "greenhouseUID": "a9jwjenfaksj",
            "controllerID": "Watering_1",
            # fields to be changed
            "lat": 32.1, # optional
            "lng": 18.3, # optional
        }
        ```
        """
        payload = request.data
        # get data

        try:
            greenhouse = GreenhouseModel.objects.get(
                uid=payload["greenhouseUID"])
        except Exception as e:
            print(e)
            print("greenhouse uid:", payload["greenhouseUID"])
            return Response({"message": "greenhouse not found"}, status=status.HTTP_204_NO_CONTENT)

        try:
            controller = ControllerModel.objects.get(
                greenhouse=greenhouse, controllerID=payload.pop("controllerID"))
        except Exception as e:
            print(e)
            print(f"contollerID: {request.data['controllerID']}")
            return Response({"message": "controller not found"}, status=status.HTTP_204_NO_CONTENT)

        # update
        ser = ControllerSerializer(
            controller, data=payload, partial=True)
        if ser.is_valid():
            ser.save()
            ret = ser.data
            ret["greenhouse"] = ser.data["greenhouse"].uid
            return Response(ret, status=status.HTTP_200_OK)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateControllerSettingAPI(APIView):
    def post(self, request):
        """
        Update the corresponding controller data from the request object

        - method: POST
        - update: update the corresponding data field in database

        #### Request format
        ```
        {
            "greenhouseUID": "a9jwjenfaksj",
            "settings": {
                "Watering_0": {
                    "on": True,
                    "manualControl": False,
                    "timestamp": "2024-04-03 17:04:04",
                    "evalveSchedules": [
                        {"cutHumidity": 12, "duration": 12, "startTime": "15:00"},
                    ]
                },
                "Watering_1": {
                    "on": True,
                    "manualControl": False,
                    "timestamp": "2024-04-03 17:04:04",
                    "evalveSchedules": [
                        {"cutHumidity": 12, "duration": 12, "startTime": "15:00"},
                    ]
                }
            }
        }
        ```
        """
        try:
            greenhouse = GreenhouseModel.objects.get(
                uid=request.data["greenhouseUID"])
        except Exception as e:
            print(f"greenhouse not found")
            return Response({"message": "greenhouse does not exist"}, status=status.HTTP_204_NO_CONTENT)

        notFound = []
        for controllerID, setting in request.data["settings"].items():
            controller = ControllerModel.objects.filter(
                greenhouse=greenhouse, controllerID=controllerID)

            if len(controller) == 0:
                print("controller not found", controllerID)
                notFound.append(controllerID)
                continue

            setting["controller"] = controller[0]
            controllerSettingSer = ControllerSettingSerializer()
            controllerSettingSer.create(setting)  # NOTE: save?

        return Response({"message": "controller updated", "notFound": notFound}, status=status.HTTP_200_OK)


class UpdateRealSensorInfoAPI(APIView):
    """
    Update the corresponding real sensor data from the request object

    - method: PATCH
    - authentication: "Authorization": "Token <token>"

   #### Request data format
   ```
   {
        "greenhouseUID": "a9jwjenfaksj",
        "realSensorID": "AirSensor",
        # fields to be changed
        "lat": 32.1, # optional
        "lng": 18.3, # optional
        "electricity": 88.2,
    }
    ```
    """

    def patch(self, request):
        payload = request.data

        # get data
        try:
            greenhouse = GreenhouseModel.objects.get(
                uid=payload.pop("greenhouseUID"))
            realSensor = RealSensorModel.objects.get(
                greenhouse=greenhouse, realSensorID=payload.pop("realSensorID"))
        except Exception as e:
            print(e)
            print(f"realSensorID: {request.data['realSensorID']}")
            return Response({"message": "real sensor does not exists"}, status=status.HTTP_204_NO_CONTENT)

        # update
        ser = RealSensorSerializer(
            realSensor, data=payload, partial=True)
        if ser.is_valid():
            ser.save()
            return Response({"message": "sensor updated"}, status=status.HTTP_200_OK)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


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
