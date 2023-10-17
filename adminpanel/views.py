from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from user.serializers import UserSerializers
from user.models import User
import jwt,datetime

# Create your views here.

class LoginView(APIView):
    def post(self,request):
        email = request.data['email']
        pasword = request.data['password']
        user = User.objects.filter(email=email).first()
        
        if not user:
            raise AuthenticationFailed('User not found!')
        
        if not user.check_password(pasword):
            raise AuthenticationFailed('Incorrect password!')
        
        if not user.is_superuser:
            raise AuthenticationFailed('Access denied!')
        
        
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
    
    
class UsersView(APIView):
    def get(selt, request):
        tocken = request.COOKIES.get('jwt')

        if not tocken:
            raise AuthenticationFailed('Unauthenticated!')
        try:
            payload = jwt.decode(tocken, 'secret', algorithms=['HS256'])
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        
        user = User.objects.all().order_by('id')
        serializer = UserSerializers(user, many = True)
        
        return Response(serializer.data)


class UserUpdateView(APIView):
    def post(self,request):
        tocken = request.COOKIES.get('jwt')
        id = request.data['id']
        if not tocken:
            raise AuthenticationFailed('Unauthenticated!')
        try:
            payload = jwt.decode(tocken, 'secret', algorithms=['HS256'])
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        
        user = User.objects.get(id=id)
         
        serializer = UserSerializers(user,data = request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        users = User.objects.all().order_by('id')
        serializer = UserSerializers(users, many = True)
        
        return Response(serializer.data)


class DeleteUserView(APIView):
    def post(self,request):
        tocken = request.COOKIES.get('jwt')
        id = request.data['id']
        if not tocken:
            raise AuthenticationFailed('Unauthenticated!')
        try:
            payload = jwt.decode(tocken, 'secret', algorithms=['HS256'])
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        
        user = User.objects.get(id=id)
        user.delete()
        
        users = User.objects.all().order_by('id')
        serializer = UserSerializers(users, many = True)
        
        return Response(serializer.data)