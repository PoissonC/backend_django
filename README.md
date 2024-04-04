# Web Service Interaction Guide

This document outlines how to interact with our web service using cURL commands. It covers the process of obtaining a CSRF token, signing up, logging in, changing the password, and logging out.

## Getting Started

Before you begin, ensure you have curl installed on your system. These commands are intended to be run in a terminal or command-line interface.

Run this command to start the server:

```
python3 manage.py runserver 0.0.0.0:PORT
```

### Obtaining a CSRF Token

To interact with the service, you first need to obtain a CSRF token by sending a request to the server. This token is used to prevent Cross-Site Request Forgery attacks.

```
curl -c cookie.txt http://host_name:port/
```
This command stores the session cookie, including the CSRF token, in cookie.txt.

Note: New version deactivates the CSRF token checks.

### Signing Up
```
curl -X POST -d "username=***&password1=********&password2=********" http://host_name:port/signup/
```
Replace CSRF_token_you_get with the actual token you received, and fill in the username, password1, and password2 fields.
### Logging In
To log in, use the following command:
```
curl " -X POST -d "username=***&password=********" http://host_name:port/login/
```
Again, replace CSRF_token_you_get with your actual token and fill in the username and password fields.

### Changing Password
To change your password, you'll need a token that is returned upon successful login. Here's how to make the request:
```
curl -X POST -H "Authorization: Token your_token" -d "current_password=********&new_password=********" http://host_name:port/change-password/
```
Replace your_token with your actual token. Fill in current_password with your current password and new_password with your new password.

### Logging Out
To log out from the service:
```
curl -X POST -H "Authorization: Token your_token" http://host_name:port/logout/
```
This command requires your login token.
