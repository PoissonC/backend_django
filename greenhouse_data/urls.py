from django.urls import path
from . import views

urlpatterns = [
    path('main-data/', views.GreenhouseMainDataAPI.as_view(),
         name='greenhouse-main-data'),
    path('create-greenhouse', views.CreatGreenhouseAPI.as_view(),
         name='greenhouse-creation'),
    path('create-real-sensor', views.CreateRealSensorAPI.as_view(),
         name="create real sensor")
]
