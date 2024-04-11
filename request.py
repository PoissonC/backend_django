import requests
import json

token = "f342d7a8444b2213a3df0dbb68abdbce195d3fb3"


def signup():
    payload = json.dumps({
        "username": "daniel",
        "email": "daniel.bb0321@gmail.com",
        "password1": "pwd",
        "password2": "pwd",
    })

    res = requests.post(
        url="http://127.0.0.1:8000/signup/",
        headers={
            "Content-Type": "application/json",
        },
        data=payload,
    )

    print(res.text)
    print(res)


def login():
    payload = json.dumps({
        "username": "daniel",
        "password": "pwd",
    })

    res = requests.post(
        url="http://127.0.0.1:8000/login/",
        headers={
            "Content-Type": "application/json",
        },
        data=payload,
    )

    print(res.text)
    print(res)


def create_greenhosue():
    payload = json.dumps({
        "name": "溫室一",
        "address": "台北市新生南路三段十巷十號二樓",
        "beginDate": "2001-03-21",
        "realSensors": [
            {
                "sensors": [
                    {
                        "sensorKey": "airHumidity",
                        "currentValue": 33,
                    },
                    {
                        "sensorKey": "airTemp",
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
                        "controllerKey": "evalve",
                        "evalveProperty": {
                            "evalveSchedules": [
                                {
                                    "cutHumidity": 33,
                                    "duration": 100,
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
                        "controllerKey": "shade",
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
            "Authorization": f"Token {token}",
        },
        data=payload,
    )

    print(res.text)
    print(res)


def create_real_sensor():
    payload = json.dumps(
        {
            "greenhouseUID": "1307f8f4-cf16-4965-996b-285fb57ff5c6",
            "nameKey": "airSensor1",
            "electricity": 100,
            "lat": 24.112,
            "lng": 47.330,
            "sensors": [
                {"index": 0, "sensorKey": "airHumidity", "currentValue": 22,
                    "timestamp": "2024-04-03 17:04:04"},
                {"index": 1, "sensorKey": "airTemp", "currentValue": 31,
                 "timestamp": "2024-04-03 17:04:04"}
            ]
        }
    )
    res = requests.post(
        url="http://127.0.0.1:8000/greenhouse/create-real-sensor",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
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
            "Authorization": f"Token {token}",
        },
    )

    print(res.text)
    print(res)


create_real_sensor()
