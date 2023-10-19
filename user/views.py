from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializers
from .models import User
import jwt,datetime
# Create your views here.

class Register(APIView):
    def post(self, request):
        email = request.data['email']
        user = User.objects.filter(email=email).first()
        
        if user:
            raise AuthenticationFailed('Email already tacken!')
        
        serializer = UserSerializers(data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        pasword = request.data['password']
        user = User.objects.filter(email=email).first()
        
        if not user:
            raise AuthenticationFailed('User not found!')
        
        if not user.check_password(pasword):
            raise AuthenticationFailed('Incorrect password!')
        
        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }
        
        tocken = jwt.encode(payload, 'secret', algorithm ='HS256')
        responce = Response()
        responce.set_cookie(key='jwt', value=tocken, httponly=True, samesite="none", secure=True)
        
        
        responce.data = {
                'jwt': tocken
            }
        
        return responce
            
class UserView(APIView):
    
    def get(selt, request):
        tocken = request.COOKIES.get('jwt')

        if not tocken:
            raise AuthenticationFailed('Unauthenticated!')
        try:
            payload = jwt.decode(tocken, 'secret', algorithms=['HS256'])
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        
        user = User.objects.get(id = payload['id'])
        serializer = UserSerializers(user)
        
        return Response(serializer.data)
    
class LogoutView(APIView):
    def post(self, request):
        tocken = request.COOKIES.get('jwt')
        response = Response()
        response.set_cookie(key='jwt', value=tocken, httponly=True, samesite="none", secure=True, max_age=0)

        response.data = {
            'message': 'success'
        }
        return response

class UpdateView(APIView):
    def post(self,request):
        tocken = request.COOKIES.get('jwt')

        if not tocken:
            raise AuthenticationFailed('Unauthenticated!')
        try:
            payload = jwt.decode(tocken, 'secret', algorithms=['HS256'])
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        
        user = User.objects.get(id = payload['id'])
        
        serializer = UserSerializers(user,data = request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)