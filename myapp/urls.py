from django.urls import path
from . import views
from .views import LoginAPIView, SignupAPIView, UserSpecificContentView
urlpatterns = [
	path('', views.index, name='home'),
	path('login/', views.user_login, name='login'),
	path('signup/', views.user_signup, name='signup'),
	path('logout/', views.user_logout, name='logout'),
	path('api/login/', LoginAPIView.as_view(), name='api-login'),
	path('api/signup/', SignupAPIView.as_view(), name='api-signup'),
	path('api/user-content/', UserSpecificContentView.as_view(), name='user-specific-content'),
]