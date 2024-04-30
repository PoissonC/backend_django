from django.urls import path
from . import greenhouse_views, app_views

urlpatterns = [
    # backend system
    path('app/delete/greenhouse', app_views.DeleteGreenhouseAPI.as_view()),
    path('app/delete/real-sensor', app_views.DeleteRealSensorAPI.as_view()),
    path('app/delete/controlelr', app_views.DeleteControllerAPI.as_view()),

    # app
    path('app', app_views.GetGreenhouseDataAPI.as_view()),
    path('app/sensors', app_views.GetSensorCurrentDataToApp.as_view()),
    path('app/controllers', app_views.GetControllerSettingToApp.as_view()),
    path('app/create/greenhouse', app_views.CreatGreenhouseAPI.as_view()),
    path('app/update/controller-info',
         app_views.UpdateControllerInfoAPI.as_view()),
    path('app/update/real-sensor', app_views.UpdateRealSensorInfoAPI.as_view()),
    path('app/update/controller-setting',
         app_views.UpdateControllerSettingAPI.as_view()),
         
    # greenhouse
    path('gh/controllers', greenhouse_views.GetAllControllerSetting.as_view()),
    path('gh/create/real-sensors', greenhouse_views.CreateRealSensorAPI.as_view()),
    path('gh/create/controllers', greenhouse_views.CreateControllerAPI.as_view()),
    path('gh/update/sensor', greenhouse_views.UpdateRealSensorDataAPI.as_view()),
]
