import requests
import json
import datetime
import random

sample_greenhouse_uid = "c8557574-3fd2-4650-90e8-e24a86851222"
host = "127.0.0.1:8000"
testing_controller_id = "evalve_3"
testing_realSensor_id = "AirSensor_4"
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
        "username": "daniel0321forever",
        "email": "daniel.bb0321@gmail.com",
        "phoneNumber": "+886 0987457321",
        "password": "pwd",
    })

    res = requests.post(
        url=f"http://{host}/auth/signup",
        headers={
            "Content-Type": "application/json",
        },
        data=payload,
    )

    return res


@api_test
def login() -> requests.Response:
    payload = json.dumps({
        "username": "daniel0321forever",
        "password": "pwd",
    })

    res = requests.post(
        url=f"http://{host}/auth/login",
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
            testing_realSensor_id: {
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
            # testing_controller_id: {
            #     "greenhouseUID": sample_greenhouse_uid,
            #     "controllerKey": "evalve",
            #     "electricity": 100,
            #     "address": {
            #         "lat": None,
            #         "lng": None,
            #     },
            #     "setting": {
            #         "on": False,
            #         "manualControl": False,
            #         "timestamp": "2024-04-03 17:04:04",
            #         "cutHumidity": 30,
            #         "schedules": [
            #                {"duration": 15, "startTime": "15:00"},
            #                {"duration": 15, "startTime": "16:00"},
            #         ],
            #     }
            # },
            "fan_1": {
                "greenhouseUID": sample_greenhouse_uid,
                "controllerKey": "fan",
                "electricity": 100,
                "address": {
                    "lat": 25.01,
                    "lng": 122.4002,
                },
                "setting": {
                    "on": False,
                    "manualControl": False,
                    "timestamp": "2024-04-03T17:04:04",
                    "openTemp": 21,
                    "closeTemp": 20,
                    "schedules": [
                        {"duration": 15, "startTime": "15:00"},
                        {"duration": 15, "startTime": "16:00"},
                    ],
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


@api_test
def create_controller_and_rSensor():
    payload = json.dumps(
        {
            "controllers": {
                testing_controller_id: {
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
                        "schedules": [
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
            },
            "realSensors": {
                testing_realSensor_id: {
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
            }
        }
    )

    return requests.post(
        url=f"http://{host}/gh/greenhouse/{sample_greenhouse_uid}",
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


@api_test
def get_sensor_history():
    res = requests.get(
        url=f"http://{host}/app/sensor/{sample_greenhouse_uid}/AirSensor_4/airHumidity?startTime=2024-05-01T22:00:00&endTime=2024-05-21T07:00:00",
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
        "realSensorID": testing_realSensor_id,
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

    res = requests.delete(
        url=f"http://{host}/app/controller/{sample_greenhouse_uid}/evalve_3",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
        },
    )

    return res


"""
greenhouse updater
"""


@api_test
def update_greenhouse():
    payload = json.dumps({
        "name": "GGHH",
        "address": "Yilan, Taiwan",
    })

    res = requests.patch(
        url=f"http://{host}/app/greenhouse/{sample_greenhouse_uid}",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
        },
        data=payload,
    )

    return res


@api_test
def update_controller_info():
    payload = json.dumps(
        {
            # fields to be changed
            "lat": 25.0285122,  # optional
            "lng": 121.5327650,  # optional
        }
    )

    res = requests.patch(
        url=f"http://{host}/app/controller/{sample_greenhouse_uid}/{testing_controller_id}",
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
                "controllerID": testing_controller_id,
                "setting": {
                    "on": True,
                    "manualControl": False,
                    "timestamp": "2024-04-03 17:04:04",
                    "cutHumidity": 21.3,
                    "schedules": [
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
            "lat": 25.0285110,
            "lng": 121.5327638,
        }
    )

    res = requests.patch(
        url=f"http://{host}/app/real-sensor/{sample_greenhouse_uid}/{testing_realSensor_id}",
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
            "AirSensor_4": {
                "realSensorID": "AirSensor_4",
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
                    "timestamp": "2024-04-18T17:04:04",
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


def update_this_month_sensor_data():
    now = datetime.datetime.now()
    startOfMonth = datetime.datetime(now.year, now.month, 1)
    _iter = startOfMonth

    while _iter < now:
        payload = json.dumps(
            {
                "AirSensor_4": {
                    "realSensorID": "AirSensor_4",
                    "electricity": 4.12,
                    "address":
                    {
                        "lat": 24.112,
                        "lng": 47.330
                    },
                    "sensors":
                    {
                        "airTemp": random.random() * 4 + 26,
                        "airHumidity": random.random() * 5 + 25,
                        "timestamp": _iter.isoformat(),
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

        print(res.status_code)
        print(res.text)

        _iter += datetime.timedelta(hours=1)


@api_test
def update_on_off():
    payload = json.dumps(
        {
            testing_controller_id: {
                "electricity": 100,
                "address": {
                    "lat": None,
                    "lng": None,
                },
                "setting": {
                    "on": False,
                    "manualControl": False,
                    "timestamp": "2024-04-03 17:04:04",
                    "cutHumidity": 30,
                    "schedules": [
                        {"duration": 15, "startTime": "15:00"},
                        {"duration": 15, "startTime": "16:00"},
                    ],
                }

            },
        }
    )

    res = requests.put(
        url=f"http://{host}/gh/controller/{sample_greenhouse_uid}",
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
    create_controller()
    # create_controller_and_rSensor()

    # get_greenhouse()
    # get_one_greenhouse()
    # get_controller_to_app()
    # get_controller_to_gre()
    # get_sensor_history()

    # update_controller_info()
    # update_controller_setting()
    # update_sensor_info()
    # update_sensor_data()
    # update_greenhouse()
    # update_on_off()
    # update_this_month_sensor_data()

    # delete_controller()
    pass
