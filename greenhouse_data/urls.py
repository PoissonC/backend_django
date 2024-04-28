from django.urls import path
from . import greenhouse_views, app_views

urlpatterns = [
    # get
    path('app', app_views.GetGreenhouseDataAPI.as_view()),
    path('app/sensors', app_views.GetSensorCurrentDataToApp.as_view()),
    path('app/controllers', app_views.GetControllerSettingToApp.as_view()),
    path('gh/controllers', greenhouse_views.GetAllControllerSetting.as_view()),
    # create
    path('create/greenhouse', greenhouse_views.CreatGreenhouseAPI.as_view()),
    path('create/real-sensors', greenhouse_views.CreateRealSensorAPI.as_view()),
    path('create/controllers', greenhouse_views.CreateControllerAPI.as_view()),
    # delete
    path('delete/greenhouse', greenhouse_views.DeleteGreenhouseAPI.as_view()),
    path('delete/real-sensor', greenhouse_views.DeleteRealSensorAPI.as_view()),
    path('delete/controlelr', greenhouse_views.DeleteControllerAPI.as_view()),
    # update
    path('update/controller-info',
         app_views.UpdateControllerInfoAPI.as_view()),
    path('update/controller-setting',
         app_views.UpdateControllerSettingAPI.as_view()),
    path('update/sensor-info', app_views.UpdateRealSensorInfoAPI.as_view()),
    path('update/sensor-data', greenhouse_views.UpdateRealSensorDataAPI.as_view()),
]
