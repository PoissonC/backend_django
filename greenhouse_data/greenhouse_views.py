from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from datetime import datetime

from .models import *
from .serializer import *

"""
TODO:
1. use parent class to separate app and greenhouse api
2. use url parameter for every api for getting information
"""


class RealSensorBaseAPI(APIView):
    def parseSensorFormat(self, sensorData: dict, realSensor=None):
        parsedSensor = {}

        # extract timestamp
        try:
            assert isinstance(sensorData, dict)
            timestamp = sensorData.pop("timestamp")
        except AssertionError as e:
            raise ValidationError(
                detail={"sensorData is not a map"}
            )
        except:
            raise ValidationError(
                detail={"timestamp is not included in sensors field"})

        # parse sensor map format
        for sensorKey, value in sensorData.items():
            try:

                parsedSensor[sensorKey] = {
                    "value": value,
                    "timestamp": timestamp,
                }

                if realSensor:
                    sensor = SensorModel.objects.get(
                        realSensor=realSensor, sensorKey=sensorKey).id
                    parsedSensor[sensorKey]['sensor'] = sensor

            except SensorModel.DoesNotExist as e:
                raise ValidationError(detail={
                                      f"senosr with sensor key {sensorKey} not found in {realSensor.realSensorID}"})

        return parsedSensor

    def parseRealSensorFormat(self, data: dict):

        try:
            for rID, rData in data.items():
                greenhouseUID = rData.setdefault("greenhouseUID", None)

                if greenhouseUID is None:
                    raise ValidationError(
                        detail={"greenhouseUID not contained in realSensor map"})

                # extract lat and lng
                assert isinstance(rData.setdefault("address", None), dict)
                address = rData.pop("address")

                # get real sensor
                try:
                    realSensor = RealSensorModel.objects.get(
                        greenhouse=greenhouseUID, realSensorID=rID)
                except RealSensorModel.DoesNotExist:
                    print("realSensor not exist, default to create mode")
                    realSensor = None

                rData["greenhouse"] = greenhouseUID
                rData["realSensorID"] = rID
                rData["realSensorKey"] = rID.split("_")[0]
                rData["lat"] = address["lat"]
                rData["lng"] = address["lng"]

                rData["sensors"] = self.parseSensorFormat(
                    rData["sensors"], realSensor)

        except AssertionError as e:
            print("address not provided")
            raise ValidationError(
                detail={"address is not included in request body"})

        except ValidationError as e:
            raise e

        except Exception as e:
            print(e)
            raise ValidationError(detail={"error parsing request body"})

        return data


class ControllerBaseAPI(APIView):
    def parseControllerFormat(self, data: dict):
        greenhouseUID = None
        try:
            assert isinstance(data, dict)
        except AssertionError as e:
            raise ValidationError(detail={"request data is not a map"})

        for controllerID, controllerData in data.items():
            try:
                assert isinstance(controllerData, dict)

                greenhouseUID = controllerData.setdefault(
                    "greenhouseUID", None)

                if greenhouseUID is None:
                    raise ValidationError(
                        detail={f"greenhouseUID not contained in realSensor map for {controllerID}"})

                controllerData["controllerID"] = controllerID
                controllerData["greenhouse"] = greenhouseUID

            except AssertionError as e:
                raise ValidationError(detail={"controller data is not a map"})

            except Exception as e:
                raise ValidationError(detail={e})

        return data


class CreateRealSensorAPI(RealSensorBaseAPI):
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

    def post(self, request):
        try:
            data = self.parseRealSensorFormat(request.data)
            for realSensorID, rSensorData in data.items():
                rSensorSer = RealSensorSerializer(data=rSensorData)

                if not rSensorSer.is_valid():
                    raise ValidationError(rSensorSer.errors)

                rSensorSer.save()

            return Response({"message": "item created"}, status=status.HTTP_200_OK)

        except RealSensorModel.DoesNotExist as e:
            print("")

        except GreenhouseModel.DoesNotExist as e:
            print(f"Greenhouse does not exist")
            return Response({"message": "Parent greenhouse not found"}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            print(e)
            return Response({"message": e.detail}, status=status.HTTP_400_BAD_REQUEST)


class CreateControllerAPI(ControllerBaseAPI):
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
        "Watering_1": {
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

    def post(self, request):
        # NOTE: we can try using PrimaryKeyField for greenhouse in serializer, so we only has to input greenhouseUID instead of an instance
        try:
            data = self.parseControllerFormat(request.data)
            for controllerData in data.values():
                controllerSer = ControllerSerializer(data=controllerData)

                if not controllerSer.is_valid():
                    raise ValidationError(detail=controllerSer.errors)

                controllerSer.save()

            return Response({"message": "item created"}, status=status.HTTP_200_OK)

        except GreenhouseModel.DoesNotExist as e:
            print(f"Greenhouse does not exist")
            return Response({"message": "Parent greenhouse not found"}, status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as e:
            print(e)
            return Response({"message": e.detail}, status=status.HTTP_400_BAD_REQUEST)


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

        # validate
        if request.data["greenhouseUID"] is None:
            return Response({"greenhouseUID field not included in request data"}, status=status.HTTP_400_BAD_REQUEST)

        if request.data["controllerID"] is None:
            return Response("controllerID is not included request data", status=status.HTTP_400_BAD_REQUEST)

        try:
            greenhouse = GreenhouseModel.objects.get(
                greenhouseUID=request.data["greenhouseUID"])
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

        except GreenhouseModel.DoesNotExist:
            print("Greenhouse not found")
            return Response({"message": "Parent greenhouse not found"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(e)
            return Response({"message": "server error occurs"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        try:
            # validate
            if request.data["greenhouseUID"] is None:
                print("greenhouseUID is not included in request data")
                return Response({"please include greenhouseUID in request data"}, status=status.HTTP_400_BAD_REQUEST)

            greenhouse = GreenhouseModel.objects.get(
                greenhouseUID=request.data.pop("greenhouseUID"))

            ret = {}

            controllers = list(
                ControllerModel.objects.filter(greenhouse=greenhouse))
            for controller in controllers:
                controllerSer = ControllerSerializer(controller)
                controllerID = controllerSer.data["controllerID"]
                controllerSer.data.setdefault("setting", None)
                ret[controllerID] = controllerSer.data["setting"]
            return Response(ret, status=status.HTTP_200_OK)

        except GreenhouseModel.DoesNotExist as e:
            print(f"Greenhouse does not exist")
            return Response({"message": "Parent greenhouse not found"}, status=status.HTTP_400_BAD_REQUEST)


class UpdateRealSensorDataAPI(RealSensorBaseAPI):
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

    def post(self, request):
        try:
            data = self.parseRealSensorFormat(request.data)

            notFound = []
            for realSensorID, realSensorData in data.items():
                print(realSensorData)
                for sensorKey, sensorValueData in realSensorData["sensors"].items():
                    print(sensorValueData)
                    sensorValueSer = SensorValueHistorySerializer(
                        data=sensorValueData)

                    # validate
                    if not sensorValueSer.is_valid():
                        raise ValidationError(sensorValueSer.errors)

                    sensorValueSer.save()

            return Response({"message": "sensor history updated", "notFound": notFound}, status=status.HTTP_200_OK)

        except RealSensorModel.DoesNotExist as e:
            print(f"real sensor not found", e)
            return Response({"message": "real sensor not found"}, status=status.HTTP_400_BAD_REQUEST)

        except GreenhouseModel.DoesNotExist as e:
            print(f"Greenhouse does not exist")
            return Response({"message": "Parent greenhouse not found"}, status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as e:
            print(e)
            return Response({"message": e.detail}, status=status.HTTP_400_BAD_REQUEST)
