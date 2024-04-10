from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from datetime import datetime
import json

from .models import GreenhouseModel
from .serializers import GreenhouseSerializer, RealControllerModel, RealSensorModel, SensorSerializer, ControllerSerializer

# Create your views here.


# TODO: first implement without serializer

class CreatGreenhouseAPI(APIView):
    # TODO: we should probably automatically create greenhouse by connecting the database with greenhouse system in given greenhouseUID
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Enable administrators to easily create a new greenhouse

        - method: POST
        - paramters: greenhouse data map
        - server: update greenhouse dataset for the user
        """
        user_id = request.user.id

        # TODO: find a way to pass in user
        payload = request.data
        payload["owner"] = user_id
        ser = GreenhouseSerializer(data=payload)

        if ser.is_valid():
            ser.save()
            return Response("greenhouse created", status=status.HTTP_201_CREATED)

        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class GreenhouseMainDataAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Return a list of greenhouseMainData map corresponding to each data in parameters

        - method: POST
        - parameters: list of greenhouse uid
        - return: list of greenhosueMainData
        """
        user = request.user  # instance ?
        greenhouses = list(GreenhouseModel.objects.filter(owner=user))

        resultList = []

        for g in greenhouses:
            gSer = GreenhouseSerializer(g)
            resultList.append(gSer.data)
        print(resultList)

        return Response(
            "testing",
            status=status.HTTP_200_OK
        )


class HistoryDataAPI(APIView):

    # TODO: not fully implemented
    def post(self, request):
        """
        Return the history data information of a sensor in specific time range.

        - method: POST
        - parameters: (greenhouseUID, sensorKey, itemIndex) -> sensorUID, startTimeStr, endTimeStr
        - return: list of history values, start date, unitScale, datelength
        """
        greenhouseUID = request.data.get("greenhouseUID")

        historyDataMap = {
            "historyValues": [],
        }

        return Response(
            historyDataMap,
            status=status.HTTP_200_OK
        )


class ControllerDataAPI(APIView):
    def patch(self, request):
        """
        Update the corresponding controller data from the request object

        - method: PATCH
        - parameters: controllerUID, controllerObjectMap
        - update: update the corresponding data field in database
        """
        return Response(status=status.HTTP_200_OK)
