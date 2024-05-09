from django.urls import path
from . import greenhouse_views, app_views

urlpatterns = [
    # backend system
    path("app/greenhouse", app_views.Greenhouse.as_view()),
    path("app/greenhouse/<greenhouseUID>",
         app_views.GreenhouseDetail.as_view()),
    path("app/controller/<greenhouseUID>/<controllerID>",
         app_views.ControllerDetail.as_view()),
    path("app/controller/<greenhouseUID>", app_views.Controller.as_view()),
    path("app/real-sensor/<greenhouseUID>/<realSensorID>",
         app_views.RealSensorAPI.as_view()),
    path("app/sensor/<greenhouseUID>/<realSensorID>/<sensorKey>",
         app_views.SensorAPI.as_view()),

    # greenhouse
    path('gh/controller/<greenhouseUID>',
         greenhouse_views.ControllerAPI.as_view()),
    path('gh/real-sensor/<greenhouseUID>',
         greenhouse_views.RealSensorAPI.as_view()),
    path('gh/greenhouse/<greenhouseUID>',
         greenhouse_views.GreenhouseAPI.as_view())
]
