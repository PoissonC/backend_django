from django.urls import path
from . import views

urlpatterns = [
    path('main-data/', views.GreenhouseMainDataAPI.as_view(),
         name='greenhouse-main-data'),
    path('create-greenhouse', views.CreatGreenhouseAPI.as_view(),
         name='greenhouse-creation'),
]
