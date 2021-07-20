from rest_framework import serializers, status, viewsets
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializers import UserSerializer

# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer


# class RegisterView(APIView):
#     def post(self, request):
#         serializer = UserSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)


# class LoginView(APIView):
#     def post(self, request):
#         email = request.data["email"]
#         password = request.data["password"]

#         user = User.objects.filter(email=email).first()

#         if user is None:
#             raise AuthenticationFailed("User not found!")

#         # if not user.check_password(password))
