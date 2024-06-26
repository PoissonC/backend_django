from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from datetime import datetime

from .models import *
from .serializer import *


class GreenhouseBaseAPI(APIView):
    """
    API for greenhouse. No permission class included
    """
    permission_classes = []


class AppBaseAPI(APIView):
    """
    API for app, required user permission
    """
    permission_classes = [IsAuthenticated]

    def checkGreenhouseOwner(self, greenhouse, user):
        print("greenhouse owner", greenhouse.owner)
        print("user", user)

        if greenhouse.owner != user:
            raise PermissionError()


class GetGreenhouseBase(AppBaseAPI):
    """
    Base class for app to get greenhouse information
    """

    def parseEvalvSchedules(self, controller):

        if controller["setting"].setdefault("schedules", None):
            scheds = controller["setting"].pop("schedules")
            for sched in scheds:
                h, m, s = sched["duration"].split(":")
                durationInSec = float(h) * 3600 + float(m) * \
                    60 + float(s)
                controller["setting"].setdefault(
                    "duration", []).append(durationInSec)
                controller["setting"].setdefault(
                    "startTime", []).append(sched["startTime"])

        return controller

    def parseToAppFormat(self, data: dict):
        realSensors = sorted(data["realSensors"],
                             key=lambda ele: ele["realSensorID"])

        data["sensors"] = {}
        data["realSensors"] = {}
        for rS in realSensors:
            sensors = rS.pop("sensors")
            data["realSensors"][rS["realSensorID"]] = rS
            for s in sensors:
                data["sensors"].setdefault(s["sensorKey"], []).append(s)

        controllers = sorted(data.pop("controllers"),
                             key=lambda ele: ele["controllerID"])

        data["controllers"] = {}
        for c in controllers:
            c["on"] = c["setting"].pop("on")
            c["manualControl"] = c["setting"].pop("manualControl")
            c = self.parseEvalvSchedules(controller=c)

            data["controllers"].setdefault(c["controllerKey"], []).append(c)

        return data


class AppControllerBaseAPI(AppBaseAPI):
    """
    Base case for app to interact with controller
    """

    def validateKey(self, controllerData):
        keysMap = {
            "evalve": ["startTime", "duration", "cutHumidity"],
            "shade": ["openTemp", "closeTemp"],
            "fan": ["openTemp", "closeTemp"]
        }
        if controllerData.setdefault("controllerID", None) is None:
            raise serializers.ValidationError({"controllerID is not defined"})

        controllerID = controllerData["controllerID"]

        if controllerData.setdefault("controllerKey", controllerID.split("_")[0]) not in keysMap.keys():
            raise serializers.ValidationError({"controllerKey is not defined"})

        for requiredKey in keysMap[controllerData["controllerKey"]]:
            if controllerData["setting"].setdefault(requiredKey, None) is None:
                raise serializers.ValidationError(
                    f"'{requiredKey}' should not be None when 'controllerKey' is '{controllerData['controllerKey']}")

    def parseInputSettingData(self, settingData):
        settingData["schedules"] = []
        durations = settingData.pop("duration", [])
        startTimes = settingData.pop("startTime", [])

        if (len(durations) != len(startTimes)):
            raise serializers.ValidationError(
                {"length of duration and startTime are not equal in request data"})

        for i in range(len(durations)):
            settingData["schedules"].append(
                {
                    "startTime": startTimes[i],
                    "duration": durations[i],
                }
            )

        return settingData

    def parseInputControllerData(self, controllerData):
        self.validateKey(controllerData)

        controllerData.setdefault("setting", {})[
            "on"] = controllerData.pop("on", None)
        controllerData.setdefault("setting", {})[
            "manualControl"] = controllerData.pop("manualControl", None)
        controllerData["setting"] = self.parseInputSettingData(
            controllerData["setting"])
        return controllerData


class RealSensorBaseAPI(GreenhouseBaseAPI):
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

    def parseRealSensorFormat(self, data: dict, greenhouseUID: str):

        rSensorList = []

        try:
            for rID, rData in data.items():

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

                rSensorList.append(rData)

        except AssertionError as e:
            print("address not provided")
            raise ValidationError(
                detail={"address is not included in request body"})

        except ValidationError as e:
            raise e

        except Exception as e:
            print(e)
            raise ValidationError(detail={"error parsing request body"})

        return rSensorList


class ControllerBaseAPI(GreenhouseBaseAPI):
    def popControllerElement(self, controllerData: dict):
        for key in ["greenhouseUID", "controllerID", "itemName"]:
            controllerData.pop(key, None)

        return controllerData

    def popSettingElement(self, controllerData: dict):
        controllerData.setdefault("setting", {}).pop("id", None)
        for sched in controllerData["setting"].setdefault(
                "schedules", {}):
            sched.pop("id", None)

        return controllerData

    def parseToControllerFormat(self, controllers):

        controllerData = {}
        for controller in controllers:
            controllerSer = ControllerSerializer(controller)
            unparsedData = controllerSer.data
            unparsedData["address"] = {
                "lat": unparsedData.pop("lat", None),
                "lng": unparsedData.pop("lng", None),
            }
            unparsedData = self.popControllerElement(unparsedData)
            unparsedData = self.popSettingElement(unparsedData)

            controllerData[controllerSer.data["controllerID"]] = unparsedData

        return controllerData

    def parseControllerFormat(self, data: dict, greenhouseUID: str):
        try:
            assert isinstance(data, dict)
        except AssertionError as e:
            raise ValidationError(detail={"request data is not a map"})

        controllerList = []

        for controllerID, controllerData in data.items():
            try:
                assert isinstance(controllerData, dict)

                if greenhouseUID is None:
                    raise ValidationError(
                        detail={f"greenhouseUID not contained in realSensor map for {controllerID}"})

                controllerData["controllerID"] = controllerID
                controllerData["greenhouse"] = greenhouseUID

                address = controllerData.pop("address", {
                    "lat": None,
                    "lng": None,
                })
                controllerData["lat"] = address["lat"]
                controllerData["lng"] = address["lng"]

                controllerList.append(controllerData)

            except AssertionError as e:
                raise ValidationError(detail={"controller data is not a map"})

            except Exception as e:
                print(e)
                raise ValidationError(detail={e})

        return controllerList
