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
            "AirSensor_1": {
                "electricity": 100,
                "lat": 24.112,
                "lng": 47.330,
                "sensors": {
                    "airHumidity": {"value": 22, "timestamp": "2024-04-03 17:04:04"},
                    "airTemp": {"value": 31, "timestamp": "2024-04-03 17:04:04"},
                }
            }
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
        try:
            user_id = request.user.id

            payload = request.data
            payload["owner"] = request.user

            ser = GreenhouseSerializer()
            greenhouse_instance = ser.create(payload)
            result = {
                "message": "greenhouse created",
                "greenhouseUID": greenhouse_instance.uid,
            }
            return Response(result, status=status.HTTP_201_CREATED)

            # TODO: use the code below for safer creation after overwriting the is_valid() method
            # ser = GreenhouseSerializer(data=payload)

            # if ser.is_valid():
            #     ser.save()
            #     result = {
            #         "message": "greenhouse created",
            #         "greenhouseUID": ser.instance.uid,
            #     }
            #     return Response(result, status=status.HTTP_201_CREATED)

            # return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            raise e


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
            return Response({"message": "please include greenhouseUID in request data"}, status=status.HTTP_400_BAD_REQUEST)

        GreenhouseModel.objects.get(uid=payload["greenhouseUID"]).delete()
        return Response({"message": "greenhouse is deleted"}, status=status.HTTP_200_OK)


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
            return Response({"message": "please include greenhouseUID in request data"}, status=status.HTTP_400_BAD_REQUEST)
        if payload["realSensorID"] is None:
            print("realSensorID is not included in request data")
            return Response({"message": "please include realSensorID in request data"}, status=status.HTTP_400_BAD_REQUEST)

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
            return Response({"message": "please include greenhouseUID in request data"}, status=status.HTTP_400_BAD_REQUEST)
        if payload["controllerID"] is None:
            print("controllerID is not included in request data")
            return Response({"message": "please include controllerID in request data"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            greenhouse = GreenhouseModel.objects.get(
                uid=payload["greenhouseUID"])
            controller = ControllerModel.objects.get(
                greenhouse=greenhouse, controllerID=payload["controllerID"])
        except Exception as e:
            print(e)
            return Response({"message": "content not found"}, status=status.HTTP_204_NO_CONTENT)

        controller.delete()
        return Response({"message": "realSensor is deleted"}, status=status.HTTP_200_OK)


"""
Get API
"""


# NOTE: not used nows
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


class GetGreenhouseDataAPI(APIView):  # TODO: check
    """
    Return a list of greenhouseMainData map for the user

    ```
    [
        {
        "greenhouseUID": "0argibdfhe",
        "name": "Greenhouse",
        "address": "Taipei, Taiwan",
        "beginTime": "2001-03-21",
        "sensors": {
          "airHumidity": [
            {
              "currentValue": 32.0,
              "itemName": "North AirSensor",
              "realSensorID": "AirSensor_1",
            },
            {
              "currentValue": 32.0,
              "itemName": "North AirSensor",
              "realSensorID": "AirSensor_2",
            },
          ],
          "soidHumidity": [
            {
              "currentValue": 32.0,
              "itemName": "North AirSensor",
              "realSensorID": "AirSensor_1",
            },
            {
              "currentValue": 32.0,
              "itemName": "North AirSensor",
              "realSensorID": "AirSensor_2",
            },
          ],
        },
        "controllers": {
          "evalve": [
            {
              "on": true,
              "manualControl": false,
              "itemName": "電磁罰1",
              "lat": 24.666,
              "lng": 25.77,
              "electricity": 0.9,
              "setting": {
                "cutHumidiy": [20.0, 30.0],
                "duration": [2.0, 3.0],
                "startTime": ["12:00:00", "14:00:00"]
              },
            },
            {
              "on": true,
              "manualControl": false,
              "itemName": "電磁罰2",
              "lat": 24.666,
              "lng": 25.77,
              "electricity": 0.9,
              "setting": {
                "cutHumidiy": [20.0, 30.0],
                "duration": [2.0, 3.0],
                "startTime": ["12:00:00", "14:00:00"]
              },
            },
          ],
          "fan": [
            {
              "on": true,
              "manualControl": false,
              "itemName": "fan",
              "lat": 24.666,
              "lng": 25.77,
              "electricity": 0.9,
              "setting": {
                "closeTemp": 32,
                "openTemp": 34,
              }
            },
            {
              "on": true,
              "manualControl": false,
              "itemName": "fan",
              "lat": 24.666,
              "lng": 25.77,
              "electricity": 0.9,
              "setting": {
                "closeTemp": 32,
                "openTemp": 34,
              }
            }
          ]
        },
        "realSensors": {
          "AirSensor_1": {"name": "My cool air sensor 1", "electricity": 0.8, "lat": 32.1, "lng": 32.1},
          "AirSensor_2": {"name": "My cool air sensor 2", "electricity": 0.8, "lat": 32.1, "lng": 32.3},
        }
      }
    ]
    ```

    - method: GET
    - authentication: "Authorization": "Token <token>"
    - return: list of greenhouseMainData
    """
    permission_classes = [IsAuthenticated]

    @staticmethod
    def parseEvalvSchedules(self, controller):

        if controller["setting"].setdefault("evalveSchedules", None):
            scheds = controller["setting"].pop("evalveSchedules")
            for sched in scheds:
                controller["setting"].setdefault(
                    "cutHumidity").append(sched["cutHumidity"])
                controller["setting"].setdefault(
                    "duration").append(sched["duration"])
                controller["setting"].setdefault(
                    "startTime").append(sched["startTime"])

        return controller

    def parseToAppFormat(self, data: dict):
        data["realSensors"] = sorted(data["realSensors"],
                                     key=lambda ele: ele["realSensorID"])

        data["sensors"] = {}
        for rS in data["realSensors"]:
            for s in rS.pop("sensors"):
                data["sensors"].setdefault(s.pop("sensorKey"), []).append(s)

        controllers = sorted(data.pop("controllers"),
                             key=lambda ele: ele["controllerID"])

        data["controllers"] = {}
        for c in controllers:
            c["on"] = c["setting"].pop("on")
            c["manualControl"] = c["setting"].pop("manualControl")
            c = self.parseEvalvSchedules(controller=c)

            data["controllers"].setdefault(c["controllerKey"], []).append(c)

        return data

    def get(self, request):
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
        "controllerKey": "evalve",
    }
    ```

    ### Return data format
    ```
    [
        {
            "on": True,
            "manualControl": False,
            "itemName": "電磁罰1",
            "settings": {
                "cutHumidiy": [20.0, 30.0],
                "duration": [2.0, 3.0],
                "startTimes": ["12:00:00", "14:00:00"]
            },
        },
        {
            "on": True,
            "manualControl": False,
            "itemName": "電磁罰2",
            "settings": {
                "cutHumidiy": [20.0, 30.0],
                "duration": [2.0, 3.0],
                "startTimes": ["12:00:00", "14:00:00"]
            },
        },
    ]
    ```
    """
    permission_classes = [IsAuthenticated]

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
        "sensorKeys": "airHumidity",
    }
    ```

    #### Return data format
    ```
    [
        {
            "currentValue: 23.1,
            "itemName": "air humidity sensor",
            "realSensorName: "AirSensor,
        },
        {
            "currentValue: 23.1,
            "itemName": "air humidity sensor",
            "realSensorName: "AirSensor,
        },
    ],


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

        # get greenhouse
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
                    "realSensorID").realSensorID
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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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
                controllerSettingSer.create(setting)

            return Response({"message": "controller updated", "notFound": notFound}, status=status.HTTP_200_OK)

        except GreenhouseModel.DoesNotExist as e:
            print(f"greenhouse not found")
            return Response({"message": "greenhouse does not exist"}, status=status.HTTP_204_NO_CONTENT)


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
    permission_classes = [IsAuthenticated]

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
