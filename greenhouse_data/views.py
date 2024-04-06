from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status


# Create your views here.


class GreenhouseMainDataAPI(APIView):
    def post(self, request):
        greenhouseUIDs = request.data.get("greenhouseUIDs")

        testMainDataList = [
            {
                "greenhouseUID": uid,
                "greenhouseName": "溫室一",
                "greenhouseAddress": "金華南路四段56巷二樓",
                "greenhouseBeginTimeStr": "20231211",
                "greenhousePhotoUrl": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR6wmOHpeGigy7bJNapLBZzilWPtZy7nK-nxDMWgpLCpg&s",
                "greenhouseRealSensorMap": {
                    "airSensor": [
                        {"currentValue": 29.0},
                        {"currentValue": 29.0},
                    ],
                },
                "greenhouseRealControllerMap": {},
                # ... more
            } for uid in greenhouseUIDs
        ]

        return Response(
            testMainDataList,
            status=status.HTTP_200_OK
        )
