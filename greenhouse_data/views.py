from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from datetime import datetime
import json

from .models import *
from .serializers import *

# TODO: implement all apis


"""
Creation API
"""


class CreatGreenhouseAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Enable administrators to easily create a new greenhouse. No sensors and controller data are sent when greenhosue is created by admin user.

        - method: POST
        - paramters: greenhouse data map
        - server: update greenhouse dataset for the user
        - return: greenhouse uid (in the same order)

        #### Post format example
        {
            "name": "test_greenhouse",
            "address": "test_address",
            "beginDate": "2011-03-21",
        }
        """
        user_id = request.user.id

        payload = request.data
        payload["owner"] = user_id
        payload["realSensors"] = []
        payload["realControllers"] = []

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
        "greenhouseUID": "1221adfadslj",
        "nameKey": "airSensor1",
        "electricity": 100,
        "lat": 24.112,
        "lng": 47.330,
        "sensors": [
            {"index": 0, "sensorKey": "airHumidity", "value": 22, "timestamp": "2024-04-03 17:04:04"}, 
            {"index": 1, "sensorKey": "airTemp", "value": 31, "timestamp": "2024-04-03 17:04:04"}
        ]
    }
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        # NOTE: we can try using PrimaryKeyField for greenhouse in serializer, so we only has to input greenhouseUID instead of an instance
        greenhouse = GreenhouseModel.objects.get(
            uid=request.data.pop("greenhouseUID"))
        payload = request.data
        payload["greenhouse"] = greenhouse
        ser = RealSensorSerializer()
        rs = ser.create(payload)

        result = {
            "message": "item created",
            "realSensorUID": rs.uid,
        }
        return Response(result, status=status.HTTP_200_OK)


class CreateRealControllerAPI(APIView):
    """
    Create controller when the creation request is sent from the controller
    """

    # UNDONE: not implemented yet
    def post(self, request):
        pass


"""
Get API
"""


class GreenhouseMainDataAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Return a list of greenhouseMainData map for the user

        - method: GET
        - authentication: "Authorization": "Token <token>"
        - return: list of greenhosueMainData
        """
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


class SensorHistoryDataAPI(APIView):

    # UNDONE: not fully implemented
    def post(self, request):
        """
        Return the history data information of a sensor in specific time range.

        - method: POST
        - authentication: "Authorization": "Token <token>"
        - return: list of history values, start date, unitScale, datelength

        #### Post datas format
        """
        greenhouseUID = request.data.get("greenhouseUID")

        historyDataMap = {
            "historyValues": [],
        }

        return Response(
            historyDataMap,
            status=status.HTTP_200_OK
        )


"""
Update API
"""


class UpdateControllerDataAPI(APIView):
    def patch(self, request):
        """
        Update the corresponding controller data from the request object

        - method: PATCH
        - parameters: controllerUID, controllerObjectMap
        - update: update the corresponding data field in database
        """
        return Response(status=status.HTTP_200_OK)


class UpdateSensorsDataAPI(APIView):
    def patch(self, request):
        pass
