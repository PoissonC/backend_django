from django.urls import path
from . import views

urlpatterns = [
    # get
    path('main-data', views.GetGreenhouseDataAPI.as_view()),
    path('basic-info', views.GetGreenhouseBasicInfoAPI.as_view()),
    path('sensors/app', views.GetSensorCurrentDataToApp.as_view()),
    path('controllers/gh', views.GetControllerSetting.as_view()),
    path('all-controller/gh', views.GetAllControllerSetting.as_view()),
    path('controllers/app', views.GetControllerSettingToApp.as_view()),
    # create
    path('create/greenhouse', views.CreatGreenhouseAPI.as_view()),
    path('create/real-sensors', views.CreateRealSensorAPI.as_view()),
    path('create/controllers', views.CreateControllerAPI.as_view()),
    # delete
    path('delete/greenhouse', views.DeleteGreenhouseAPI.as_view()),
    path('delete/real-sensor', views.DeleteRealSensorAPI.as_view()),
    path('delete/controlelr', views.DeleteControllerAPI.as_view()),
    # update
    path('update/controller-info', views.UpdateControllerInfoAPI.as_view()),
    path('update/controller-setting', views.UpdateControllerSettingAPI.as_view()),
    path('update/sensor-info', views.UpdateRealSensorInfoAPI.as_view()),
    path('update/sensor-data', views.UpdateRealSensorDataAPI.as_view()),
]
