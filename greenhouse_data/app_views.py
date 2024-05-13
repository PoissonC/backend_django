from rest_framework.response import Response
from rest_framework import status
from django.core import exceptions
from statistics import fmean

from .models import *
from .serializer import *
from .api_base import *


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
    """

    # UNDONE: need api for updating greenhouse

    def patch(self, req, greenhouseUID):  # NOTE: new api
        """
        Update greenhouse information
        """

        try:
            user = req.user
            payload = req.data
            greenhouse = GreenhouseModel.objects.get(
                greenhouseUID=greenhouseUID)

            self.checkGreenhouseOwner(greenhouse, user)

            ser = GreenhouseSerializer(greenhouse, data=payload, partial=True)
            if ser.is_valid():
                greenhouse_instance = ser.save()
                result = {
                    "message": "greenhouse updated",
                    "greenhouseUID": greenhouse_instance.greenhouseUID,
                }
                return Response(result, status=status.HTTP_201_CREATED)

            print("validation error:", ser.errors)
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        except GreenhouseModel.DoesNotExist:
            print("greenhouse not found")
            return Response("greenhouse not found", status=status.HTTP_404_NOT_FOUND)
        except PermissionError as e:
            print("validation errors", e)
            return Response({"error": "you don't have the access to the greenhouse"}, status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, greenhouseUID):
        """
        Delete the greenhouse with uid == greenhouseUID

        - method: DELETE
        - authentication: "Authorization"" "Token <token>"
        """

        GreenhouseModel.objects.get(uid=greenhouseUID).delete()
        return Response({"message": "greenhouse is deleted"}, status=status.HTTP_200_OK)

    def get(self, req, greenhouseUID):
        """
        Get information for one specific greenhouse
        """
        try:
            greenhouse = GreenhouseModel.objects.get(
                greenhouseUID=greenhouseUID)

            ser = GreenhouseSerializer(greenhouse)
            greenhouseData = self.parseToAppFormat(ser.data)
            return Response(greenhouseData, status=status.HTTP_200_OK)

        except GreenhouseModel.DoesNotExist:
            return Response({"error": "greenhouse does not exist"}, status=status.HTTP_404_NOT_FOUND)


class Controller(AppControllerBaseAPI):
    """
    API to get all controllers in a greenhouse
    """

    def get(self, request, greenhouseUID):
        """ Get all controller in the greenhouse"""
        try:
            user = request.user
            greenhouse = GreenhouseModel.objects.get(
                greenhouseUID=greenhouseUID)

            self.checkGreenhouseOwner(greenhouse, user)

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
            user = req.user
            greenhouse = GreenhouseModel.objects.get(
                greenhouseUID=greenhouseUID)

            self.checkGreenhouseOwner(greenhouse, user)

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

        try:
            greenhouse = GreenhouseModel.objects.get(
                greenhouseUID=greenhouseUID)
            controller = ControllerModel.objects.get(
                greenhouse=greenhouse, controllerID=controllerID)

            controller.delete()
            return Response({"message": "realSensor is deleted"}, status=status.HTTP_200_OK)
        except GreenhouseModel.DoesNotExist:
            print(f"greenhouse {greenhouseUID} not found")
            return Response({"message": "greenhouse not found"}, status=status.HTTP_404_NOT_FOUND)
        except ControllerModel.DoesNotExist:
            print(f"controllerID {controllerID} not found")
            return Response({"message": f"controllerID {controllerID} not found"}, status=status.HTTP_404_NOT_FOUND)


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
        except RealSensorModel.DoesNotExist:
            print(f"realsensor {realSensorID} not found")
            return Response({"error": f"realSensor {realSensorID} not found"}, status=status.HTTP_404_NOT_FOUND)
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
    def findUnitScale(self, startTime: datetime.datetime, endTime: datetime.datetime, labelScale=3):
        hoursDiff = endTime - startTime
        hoursDiff = int(hoursDiff.days * 24 + hoursDiff.seconds // 3600)

        if (hoursDiff < 12 * labelScale):
            unitScale = 1
        elif (hoursDiff >= 12 * labelScale and hoursDiff < 24 * labelScale):
            unitScale = 2
        elif (hoursDiff >= 24 * labelScale and hoursDiff < 36 * labelScale):
            unitScale = 3
        elif (hoursDiff >= 36 * labelScale and hoursDiff < 48 * labelScale):
            unitScale = 4
        elif (hoursDiff >= 48 * labelScale and hoursDiff < 72 * labelScale):
            unitScale = 6
        elif (hoursDiff >= 72 * labelScale and hoursDiff < 144 * labelScale):
            unitScale = 12
        elif (hoursDiff >= 144 * labelScale):
            unitScale = 24 * (hoursDiff // (24 * 4 * labelScale))
        else:
            print(f"ERROR: negative hourDiff. hoursDiff={hoursDiff}")
            raise ValidationError(
                {f"ERROR: negative hourDiff. hoursDiff={hoursDiff}"})

        return unitScale

    def hourly(self, startTime: datetime, endTime: datetime, delta=datetime.timedelta(hours=1)):
        currentTime = startTime
        while currentTime <= endTime and currentTime < datetime.datetime.now():
            yield currentTime
            currentTime += delta

    def findHourlyData(self, historyInstances, startTime: datetime, endTime: datetime):
        hourlyData = []
        lastData = None
        broken = False

        for t in self.hourly(startTime=startTime, endTime=endTime):
            timeInstance = list(historyInstances.filter(
                timestamp__range=[
                    t-datetime.timedelta(minutes=15),
                    t+datetime.timedelta(minutes=15),
                ]
            ))

            if len(timeInstance) > 0:
                print("get time instance")
                hourlyData.append(timeInstance[0].value)
                lastData = hourlyData[-1]
                continue

            if lastData:
                print("using last data")
                hourlyData.append(lastData)
                lastData = hourlyData[-1]
                continue

            print(f"finding data at {t} from future instances")
            broken = True
            break

        if broken:
            t = t+datetime.timedelta(hours=1)
            nextDatas = self.findHourlyData(historyInstances, t, endTime)
            hourlyData += [nextDatas[0]]
            hourlyData += nextDatas

        return hourlyData

    # UNDONE: not fully implemented

    def get(self, request, greenhouseUID, realSensorID, sensorKey):
        """
        Return the history data information of a sensor in specific time range.

        - method: POST
        - authentication: "Authorization": "Token <token>"
        - return: list of history values, start date, unitScale, datelength

        #### Parameters
        - startTime: "YYYY-MM-DD HH:mm:ss"
        - endTime: "YYYY-MM-DD HH:mm:ss" 

        #### Return data format
        {
            "historyDatas": [19, 20.1, 33.2, 21.3],
            "initialDateTime": "2024-03-21 00:00:00",
            "unitScale": 2, # 2 hours
        }
        """
        try:
            # get start time and end time
            startTime = request.query_params.get("startTime")
            endTime = request.query_params.get("endTime")

            if startTime is None:
                return Response({"error": "please provide startTime in query"}, status=status.HTTP_400_BAD_REQUEST)
            if endTime is None:
                return Response({"error": "please provide endTime in query"}, status=status.HTTP_400_BAD_REQUEST)

            startTime = datetime.datetime.fromisoformat(startTime)
            endTime = datetime.datetime.fromisoformat(endTime)

            # get history instances
            greenhouse = GreenhouseModel.objects.get(
                greenhouseUID=greenhouseUID)
            realSensor = RealSensorModel.objects.get(
                greenhouse=greenhouse,
                realSensorID=realSensorID,
            )
            sensor = SensorModel.objects.get(
                realSensor=realSensor, sensorKey=sensorKey)
            historyInstances = SensorValueHistoryModel.objects.filter(
                sensor=sensor,
                timestamp__range=[startTime, endTime],
            )

            if len(historyInstances) == 0:
                return Response({"message": "no history found"}, status=status.HTTP_204_NO_CONTENT)

            """
            TODO: design an algorithm to acheive following goals
            - find suitable unitScale for the timerange
            - check if data exist in each hour
            - replace missing data with the last element value in the list
            - if we cannot find the existing data until the start of the list, try getting the next data instead
            - if we still cannot find any existing data until the end of the list, return no_value respond 
            """
            historyDatas = []
            unitScale = self.findUnitScale(startTime, endTime)
            hourlyData = self.findHourlyData(
                historyInstances, startTime, endTime)

            i = 0
            while i < len(hourlyData):
                if (i + unitScale) <= len(hourlyData):
                    historyDatas.append(fmean(hourlyData[i:i+unitScale]))
                    i += unitScale
                else:
                    historyDatas.append(fmean(hourlyData[i:]))
                    break

            return Response(
                {
                    "historyDatas": historyDatas,
                    "initialTime": startTime.isoformat(),
                    "unitScale": unitScale,
                },
                status=status.HTTP_200_OK,
            )

        except GreenhouseModel.DoesNotExist:
            print(f"greenhouse {greenhouseUID} not found")
            return Response({"message": "greenhouse not found"}, status=status.HTTP_404_NOT_FOUND)
        except RealSensorModel.DoesNotExist:
            print(f"real sensor {realSensorID} not found")
            return Response({"errors": f"realSensor {realSensorID} not found"}, status=status.HTTP_404_NOT_FOUND)
        except SensorModel.DoesNotExist:
            print(f"sensor {sensorKey} not found")
            return Response({"errors": f"sensorKey: {sensorKey} not found"}, status=status.HTTP_404_NOT_FOUND)
