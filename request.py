import requests
import json
import datetime

sample_greenhouse_uid = "cb91a232-d989-487b-970d-ae717352281b"
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
                json.dump(object, f, indent=2, ensure_ascii=False)
                return object
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
        url=f"http://{host}/auth/signup/",
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
        url=f"http://{host}/auth/login/",
        headers={
            "Content-Type": "application/json",
        },
        data=payload,
    )

    return res


try:
    token = login()["token"]

except Exception as e:
    print(e)
    signup()
    token = login()["token"]


"""
greenhouse creation
"""


@api_test
def create_greenhouse() -> requests.Response:
    payload = json.dumps(
        {
            "name": "GH2",
            "address": "Taipei, Taiwan",
            "beginDate": "2011-03-21",
            "realSensors": {
                "AirSensor_0": {
                    "electricity": 97,
                    "realSensorKey": "AirSensor",
                    "lat": 24.112,
                    "lng": 47.330,
                    "sensors": {
                        "airHumidity": {"value": 22, "timestamp": "2024-04-03 17:04:04"},
                        "airTemp": {"value": 31, "timestamp": "2024-04-03 17:04:04"},
                    }
                },
                "AirSensor_1": {
                    "electricity": 100,
                    "realSensorKey": "AirSensor",
                    "lat": 24.112,
                    "lng": 47.330,
                    "sensors": {
                        "airHumidity": {"value": 22, "timestamp": "2024-04-03 17:04:04"},
                        "airTemp": {"value": 31, "timestamp": "2024-04-03 17:04:04"},
                    }
                }
            },
            "controllers": {
                "evalve_0": {
                    "controllerKey": "evalve",
                    "electricity": 100,
                    "lat": 24.112,
                    "lng": 47.330,
                    "setting": {
                        "on": True,
                        "manualControl": False,
                        "cutHumidity": 30,
                        "evalveSchedules": [
                            {"duration": 15, "startTime": "15:00"},
                            {"duration": 15, "startTime": "16:00"},
                        ],
                        "timestamp":  "2024-04-03 17:04:04",
                    },

                },
                "shade_0": {
                    "controllerKey": "shade",
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
                },
                "fan_0": {
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
    )

    res = requests.post(
        url=f"http://{host}/app/greenhouse",
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
            "AirSensor_4": {
                "greenhouseUID": sample_greenhouse_uid,
                "realSensorKey": "AirSensor",
                "electricity": 4.12,
                "address":
                {
                    "lat": 24.112,
                    "lng": 47.330
                },
                "sensors":
                {
                    "airTemp": 20.1,
                    "airHumidity": 68.9,
                    "timestamp": "2024-04-18 17:04:04"
                }
            },
        },
    )
    res = requests.post(
        url=f"http://{host}/gh/real-sensor/{sample_greenhouse_uid}",
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
            "evalve_3": {
                "greenhouseUID": sample_greenhouse_uid,
                "controllerKey": "evalve",
                "electricity": 100,
                "lat": 24.112,
                "lng": 47.330,
                "setting": {
                    "on": False,
                    "manualControl": False,
                    "timestamp": "2024-04-03 17:04:04",
                    "cutHumidity": 30,
                    "evalveSchedules": [
                           {"duration": 15, "startTime": "15:00"},
                           {"duration": 15, "startTime": "16:00"},
                    ],
                }
            },
            "fan_3": {
                "greenhouseUID": sample_greenhouse_uid,
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
    )

    return requests.post(
        url=f"http://{host}/gh/controller/{sample_greenhouse_uid}",
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
        url=f"http://{host}/app/greenhouse",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
        },
    )

    return res


@api_test
def get_one_greenhouse() -> requests.Response:
    res = requests.get(
        url=f"http://{host}/app/greenhouse/{sample_greenhouse_uid}",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
        },
    )

    return res


@api_test
def get_controller_to_gre() -> requests.Response:
    res = requests.get(
        url=f"http://{host}/gh/controller/{sample_greenhouse_uid}",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
        },
    )

    return res


@api_test
def get_controller_to_app() -> requests.Response:

    res = requests.get(
        url=f"http://{host}/app/controller/{sample_greenhouse_uid}",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
        },
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
        "controllerID": "evalve_1",
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
            # fields to be changed
            "lat": 32.1,  # optional
            "lng": 18.3,  # optional
        }
    )

    res = requests.patch(
        url=f"http://{host}/app/controller/{sample_greenhouse_uid}/Watering_0",
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
        [
            {
                "controllerID": "Watering_0",
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
    )

    res = requests.put(
        url=f"http://{host}/app/controller/{sample_greenhouse_uid}",
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
            # fields to be changed
            "lat": 32.1,  # optional
            "lng": 18.3,  # optional
        }
    )

    res = requests.patch(
        url=f"http://{host}/app/realSensor/{sample_greenhouse_uid}/AirSensor_1",
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
            "AirSensor_1": {
                "greenhouseUID": sample_greenhouse_uid,
                "realSensorKey": "AirSensor",
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
                    "timestamp": "2024-04-18 17:04:04"
                }
            },
        }
    )

    res = requests.put(
        url=f"http://{host}/gh/real-sensor/{sample_greenhouse_uid}",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
        },
        data=payload,
    )

    return res


if __name__ == '__main__':
    # create_greenhouse()
    # create_real_sensor()
    # create_controller()

    # get_greenhouse()
    # get_one_greenhouse()
    # get_controller_to_app()
    # get_controller_to_gre()

    update_controller_info()
    update_controller_setting()
    # update_sensor_info()
    # update_sensor_data()
    pass
