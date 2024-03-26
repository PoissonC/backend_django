from django.shortcuts import render

# Create your views here.
from django.contrib.auth import authenticate, login, logout 
from .forms import SignupForm, LoginForm
from django.http import JsonResponse, HttpResponse
from django.middleware.csrf import get_token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from rest_framework.permissions import IsAuthenticated

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
	def post(self, request, *args, **kwargs):
		username = request.data.get("username")
		email = request.data.get("email")
		password1 = request.data.get("password1")
		password2 = request.data.get("password2")
		if not username or not email or not password1 or not password2:
			return Response({"error": "Username, email, password, and password confirmation are required."}, status=status.HTTP_400_BAD_REQUEST)
		if password1 != password2:
			return Response({"error": "input passwords are not the same"}, status=status.HTTP_400_BAD_REQUEST)
		if User.objects.filter(username=username).exists():
			return Response({"error": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)

		# Create the user
		user = User.objects.create(
			username=username,
			email=email,
			password=make_password(password1)  # Hash the password
		)
		
		# Automatically generate a token for the new user
		token = Token.objects.create(user=user)
		
		return Response({"token": token.key, "user_id": user.id, "username": user.username}, status=status.HTTP_201_CREATED)

class LoginAPIView(APIView):
	def post(self, request, *args, **kwargs):
		username = request.data.get("username")
		password = request.data.get("password")
		user = authenticate(username=username, password=password)
		if not username or not password:
			return Response({"error": "Missing username or password."}, status=status.HTTP_400_BAD_REQUEST)
		if user:
			# Delete any existing token for the user and create a new one
			Token.objects.filter(user=user).delete()
			token = Token.objects.create(user=user)
			return Response({"token": token.key}, status=status.HTTP_200_OK)
		else:
			return Response({"error": "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST)

# Home page
def index(request):
	if request.method == 'GET':
	# Return CSRF token in JSON response
		return JsonResponse({'csrfToken': get_token(request)})
	else:
		return HttpResponse("fuck off!\n")

# signup page

#return value can be discussed

def user_signup(request):
	if request.method == 'POST':
		print(request.POST)
		if 'username' in request.POST and 'password1' in request.POST and 'password2' in request.POST:
			if request.POST['password1'] == request.POST['password2']:
				return HttpResponse("Success!\n")
			else:
				return HttpResponse("Fail!\n")
	return JsonResponse({'csrfToken': get_token(request)})

# login page
def user_login(request):
	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			user = authenticate(request, username=username, password=password)
			if user:
				login(request, user)    
				return redirect('home')
	else:
		form = LoginForm()
	return render(request, 'login.html', {'form': form})

# logout page
def user_logout(request):
	logout(request)
	return redirect('login')