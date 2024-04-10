import requests
import json


def create_greenhosue():
    payload = json.dumps({
        "name": "test_greenhouse",
        "address": "test_address",
        "beginDateStr": "2001-03-21",
        "realSensors": [
            {
                "sensors": [
                    {
                        "currentValue": 33,
                    },
                    {
                        "currentValue": 18,
                    }
                ],
                "nameKey": "coolItem",
                "electricity": 10,
                "lat": 24,
                "lng": 80,
            },
        ],
        "realControllers": [
            {
                "controllers": [
                    {
                        "on": False,
                        "manual": False,
                        "evalveProperty": {
                            "evalveSchedules": [
                                {
                                    "cutHumidity": 33,
                                    "duration": 10,
                                    "startTime": "13:30",
                                }
                            ]
                        },
                        "shadeProperty": None,
                        "fanProperty": None,
                    },
                    {
                        "on": False,
                        "manual": False,
                        "evalveProperty": None,
                        "shadeProperty": {
                            "openTemp": 33,
                            "closeTemp": 20,
                        },
                        "fanProperty": None,
                    }
                ],
                "nameKey": "coolController",
                "electricity": 10,
                "lat": 24,
                "lng": 80,
            },
        ]
    })

    res = requests.post(
        url="http://127.0.0.1:8000/greenhouse/create-greenhouse",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Token 9862ffc4db638058bd54e424dc06be1e976563e3",
        },
        data=payload,
    )

    print(res.text)
    print(res)


def get_greenhouse():
    res = requests.get(
        url="http://127.0.0.1:8000/greenhouse/main-data",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Token 9862ffc4db638058bd54e424dc06be1e976563e3",
        },
    )

    print(res.text)
    print(res)


get_greenhouse()
