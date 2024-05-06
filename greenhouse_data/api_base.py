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


class GetGreenhouseBase(AppBaseAPI):
    """
    Base class for app to get greenhouse information
    """

    def parseEvalvSchedules(self, controller):

        if controller["setting"].setdefault("evalveSchedules", None):
            scheds = controller["setting"].pop("evalveSchedules")
            for sched in scheds:
                controller["setting"].setdefault(
                    "duration", []).append(sched["duration"])
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


class ControllerBaseAPI(GreenhouseBaseAPI):
    def parseControllerFormat(self, data: dict, greenhouseUID: str):
        try:
            assert isinstance(data, dict)
        except AssertionError as e:
            raise ValidationError(detail={"request data is not a map"})

        for controllerID, controllerData in data.items():
            try:
                assert isinstance(controllerData, dict)

                if greenhouseUID is None:
                    raise ValidationError(
                        detail={f"greenhouseUID not contained in realSensor map for {controllerID}"})

                controllerData["controllerID"] = controllerID
                controllerData["greenhouse"] = greenhouseUID

            except AssertionError as e:
                raise ValidationError(detail={"controller data is not a map"})

            except Exception as e:
                print(e)
                raise ValidationError(detail={e})

        return data
