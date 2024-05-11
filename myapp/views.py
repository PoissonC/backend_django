
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
from django.contrib.auth import authenticate
from django.http import JsonResponse, HttpResponse
from django.middleware.csrf import get_token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status


from rest_framework.permissions import IsAuthenticated
from .serializers import *
from .models import *


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Delete the token to log out
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            # Check old password
            if not user.check_password(serializer.validated_data['current_password']):
                return Response({"current_password": ["Wrong password."]},
                                status=status.HTTP_400_BAD_REQUEST)
            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ValidatePermission(APIView):
    permission_classes = [IsAuthenticated]

    def post(sefl, req):
        user = req.user


class UserSpecificContentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        # Access the user from the request
        user = request.user

        # Generate or retrieve content specific to the user
        # For demonstration, we'll just return the user's username and email
        content = {
            'message': 'This is your user-specific content.',
            'username': user.username,
            'email': user.email,
        }

        return Response(content)


class SignupAPIView(APIView):

    # @method_decorator(csrf_exempt)
    # def dispatch(self, *args, **kwargs):
    # 	return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Sign up to create an user

        #### Request format
        ```
        {
            "username": "daniel",
            "password": "pwd",
            "email": "daniel.bb0321@gmail.com",
            "phoneNumber": "0987457321",
        }
        ```
        """
        user = None

        try:
            serializer = UserRegistrationSerializer(data={
                "username": request.data.setdefault("username", None),
                "email": request.data.setdefault("email", None),
                "password": request.data.setdefault("password", None),
            })

            if not serializer.is_valid():
                print(serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            user = serializer.save()  # The user is created and saved here
            # Retrieve the token created for the user

            userInfoSer = UserInforSerializer(data={
                "user": user.id,
                "Email": request.data.setdefault("email", None),
                "phoneNumber": request.data.setdefault("phoneNumber", None),
            })

            if not userInfoSer.is_valid():
                user.delete()
                print(serializer.errors)
                return Response(userInfoSer.errors, status=status.HTTP_400_BAD_REQUEST)

            userInfoSer.save()

            token = Token.objects.get(user=user)

            return Response({"token": token.key, "user_id": user.id, "username": user.username}, status=status.HTTP_201_CREATED)

        except Exception as e:
            if user is not None:
                user.delete()
            raise e


class LoginAPIView(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if not username or not password:
            return Response({"username": "not found"}, status=status.HTTP_403_FORBIDDEN)
        if user:
            # Delete any existing token for the user and create a new one
            Token.objects.filter(user=user).delete()
            token = Token.objects.create(user=user)

            # return user information
            userInfo = UserInformationModel.objects.get(user=user)
            userInfoData = UserInforSerializer(userInfo).data

            return Response({"token": token.key, "user": userInfoData}, status=status.HTTP_200_OK)
        else:
            print("Invalid credential")
            return Response({"password": "invalid"}, status=status.HTTP_400_BAD_REQUEST)

# Home page


def index(request):
    if request.method == 'GET':
        # Return CSRF token in JSON response
        return JsonResponse({'csrfToken': get_token(request)})
    else:
        return HttpResponse("fuck off!\n")
