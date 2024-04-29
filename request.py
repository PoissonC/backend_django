import requests
import json
import datetime

token = "ecd712ae12b99b1aac2cac879b353eba4f332358"
# token = "e0a8616dda7c0cf5f3451b60b430f4e19274ce4a"
sample_greenhouse_uid = "70c8a4d7-019e-433b-8491-200ef4a33d48"
# sample_greenhouse_uid = "f3d3072f-b666-4aeb-b920-8a97a59cf713"

host = "127.0.0.1:8000"
# host = "123.193.99.66:9000"


def api_test(func):
    def wrap():
        res: requests.Response = func()
        print(res.text)
        print(res)

        try:
            object = json.loads(res.text)
            with open("result.json", "w") as f:
                json.dump(object, f, indent=2)
        except Exception as e:
            print(e)
    return wrap


"""
authentication
"""


@api_test
def signup() -> requests.Response:
    payload = json.dumps({
        "username": "daniel",
        "email": "daniel.bb0321@gmail.com",
        "password1": "pwd",
        "password2": "pwd",
    })

    res = requests.post(
        url=f"http://{host}/signup/",
        headers={
            "Content-Type": "application/json",
        },
        data=payload,
    )

    return res


@api_test
def login() -> requests.Response:
    payload = json.dumps({
        "username": "daniel",
        "password": "pwd",
    })

    res = requests.post(
        url=f"http://{host}/login/",
        headers={
            "Content-Type": "application/json",
        },
        data=payload,
    )

    return res


"""
greenhouse creation
"""


@api_test
def create_greenhosue() -> requests.Response:
    payload = json.dumps({
        "name": "溫室一",
        "address": "台北市新生南路三段十巷十號二樓",
        "beginDate": "2001-03-21",
    })

    res = requests.post(
        url=f"http://{host}/greenhouse/app/create/greenhouse",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
        },
        data=payload,
    )

    return res


@api_test
def create_real_sensor() -> requests.Response:
    payload = json.dumps(
        {
            "greenhouseUID": sample_greenhouse_uid,
            "realSensors": {
                "AirSensor_0": {
                    "electricity": 100,
                    "lat": 24.112,
                    "lng": 47.330,
                    "sensors": {
                        "airHumidity": {"value": 22, "timestamp": "2024-04-03 17:04:04"},
                        "airTemp": {"value": 31, "timestamp": "2024-04-03 17:04:04"},
                    }
                },
                "AirSensor_1": {
                    "electricity": 100,
                    "lat": 24.112,
                    "lng": 47.330,
                    "sensors": {
                        "airHumidity": {"value": 22, "timestamp": "2024-04-03 17:04:04"},
                        "airTemp": {"value": 31, "timestamp": "2024-04-03 17:04:04"},
                    }
                }
            },
        }
    )
    res = requests.post(
        url=f"http://{host}/greenhouse/gh/create/real-sensors",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
        },
        data=payload,
    )

    return res


@api_test
def create_controller() -> requests.Response:
    payload = json.dumps(
        {
            "greenhouseUID": sample_greenhouse_uid,
            "controllers": {
                "Watering_0": {
                    "controllerKey": "evalve",
                    "electricity": 100,
                    "lat": 24.112,
                    "lng": 47.330,
                    "setting": {
                        "on": False,
                        "manualControl": False,
                        "timestamp": "2024-04-03 17:04:04",
                        "evalveSchedules": [
                            {"cutHumidity": 30, "duration": 15,
                                "startTime": "15:00"},
                            {"cutHumidity": 30, "duration": 15,
                                "startTime": "16:00"},
                        ],
                    }
                },
                "Fan_0": {
                    "controllerKey": "fan",
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
        }
    )

    return requests.post(
        url=f"http://{host}/greenhouse/gh/create/controllers",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
        },
        data=payload,
    )


"""
greenhouse getter
"""


@api_test
def get_greenhouse() -> requests.Response:
    res = requests.get(
        url=f"http://{host}/greenhouse/app",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
        },
    )

    return res


@api_test
def get_sensor() -> requests.Response:
    payload = json.dumps(
        {
            "greenhouseUID": sample_greenhouse_uid,
            "sensorKeys": ["airHumidity"],
        }
    )
    res = requests.post(
        url=f"http://{host}/greenhouse/app/sensors",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
        },
        data=payload
    )

    return res


@api_test
def get_controller_to_gre() -> requests.Response:
    payload = json.dumps(
        {
            "greenhouseUID": sample_greenhouse_uid,
            "controllerID": ["Watering_0"],
        }
    )
    res = requests.post(
        url=f"http://{host}/greenhouse/gh/controllers",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
        },
        data=payload,
    )

    return res


@api_test
def get_controller_to_app() -> requests.Response:
    payload = json.dumps(
        {
            "greenhouseUID": sample_greenhouse_uid,
            "controllerID": ["Watering_0"],
        }
    )
    res = requests.post(
        url=f"http://{host}/greenhouse/app/controllers",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
        },
        data=payload
    )

    return res


"""
greenhouse deleter
"""


@api_test
def delete_greenhouse():
    payload = json.dumps({
        "greenhouseUID": sample_greenhouse_uid
    })

    res = requests.delete(
        url=f"http://{host}/greenhouse/app/delete/greenhouse",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
        },
        data=payload,
    )

    return res


@api_test
def delete_real_sensor():
    payload = json.dumps({
        "greenhouseUID": sample_greenhouse_uid,
        "realSensorID": "AirSensor_1",
    })

    res = requests.delete(
        url=f"http://{host}/greenhouse/app/delete/real-sensor",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
        },
        data=payload,
    )

    return res


@api_test
def delete_controller():
    payload = json.dumps({
        "greenhouseUID": sample_greenhouse_uid,
        "controllerID": "Watering_1",
    })

    res = requests.delete(
        url=f"http://{host}/greenhouse/app/delete/controller",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
        },
        data=payload,
    )

    return res


"""
greenhouse updater
"""


@api_test
def update_controller_info():
    payload = json.dumps(
        {
            "greenhouseUID": sample_greenhouse_uid,
            "controllerID": "Watering_0",
            # fields to be changed
            "lat": 32.1,  # optional
            "lng": 18.3,  # optional
        }
    )

    res = requests.patch(
        url=f"http://{host}/greenhouse/app/update/controller-info",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
        },
        data=payload,
    )

    return res


@api_test
def update_controller_setting():
    payload = json.dumps(
        {
            "greenhouseUID": sample_greenhouse_uid,
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
    )

    res = requests.post(
        url=f"http://{host}/greenhouse/app/update/controller-setting",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
        },
        data=payload,
    )

    return res


@api_test
def update_sensor_info():
    payload = json.dumps(
        {
            "greenhouseUID": sample_greenhouse_uid,
            "realSensorID": "AirSensor_0",
            # fields to be changed
            "lat": 32.1,  # optional
            "lng": 18.3,  # optional
            "electricity": 88.2,
        }
    )

    res = requests.patch(
        url=f"http://{host}/greenhouse/app/update/sensor-info",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
        },
        data=payload,
    )

    return res


@api_test
def update_sensor_data():
    payload = json.dumps(
        {
            "greenhouseUID": sample_greenhouse_uid,
            "realSensors": {
                "AirSensor_0": {
                    "airHumidity": {"value": 22, "timestamp": "2024-04-03 17:04:04"},
                    "airTemp": {"value": 31, "timestamp": "2024-04-03 17:04:04"},
                },
                "AirSensor_1": {
                    "airHumidity": {"value": 22, "timestamp": "2024-04-03 17:04:04"},
                    "airTemp": {"value": 31, "timestamp": "2024-04-03 17:04:04"},
                }
            },
        }
    )

    res = requests.post(
        url=f"http://{host}/greenhouse/gh/update/sensor-data",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
        },
        data=payload,
    )

    return res


get_controller_to_app()
