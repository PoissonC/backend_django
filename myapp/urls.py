from django.urls import path
from . import views
from .views import LoginAPIView, SignupAPIView, UserSpecificContentView, ChangePasswordView, LogoutAPIView

urlpatterns = [
    path('', views.index, name='home'),
    path('login/', LoginAPIView.as_view(), name='api-login'),
    path('signup/', SignupAPIView.as_view(), name='api-signup'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('user-content/', UserSpecificContentView.as_view(),
         name='user-specific-content'),
    path('logout/', LogoutAPIView.as_view(), name='api-logout'),
]
