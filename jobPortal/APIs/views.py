from django.http import Http404
from django.shortcuts import render
from rest_framework import generics, status
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import *
from .serializers import *


@api_view(['POST'])
#@permission_classes([IsAuthenticated])
def CreateProfile(request):

    if request.method == 'POST':
        try:
            serializer_class = ProfileSerializer(data=request.data)
            if serializer_class.is_valid():
                serializer_class.save()
                return Response({'action': "Add Profile", 'message': "Profile Added Successfully"},
                                status=status.HTTP_200_OK)
            else:
                return Response({'action': "Add Profile", 'message': serializer_class.errors},
                                status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'action': "Add Profile", 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def signUp(request):
    if request.method == 'POST':

        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
                serializer.save()
                return Response({'action': "Add New User", 'message': "User Added Successfully"},
                                status=status.HTTP_200_OK)
            else:
                return Response({'action': "Add User", 'message': serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'action': "Add User", 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
#@permission_classes([IsAuthenticated])
def login(request):
    print(request.data)
    try:
        username = request.data['username']
        password = request.data['password']
        user = get_object_or_404(CustomUser, username=username)

        if check_password(password, user.password):

            return Response({
                'action': "Login",
                'message': "Login Successful",
                'data': {
                    'id': user.id
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({'action': "Login", 'message': "Incorrect Password"}, status=status.HTTP_401_UNAUTHORIZED)

    except Http404:
        return Response({'action': "Get Login", 'message': 'User Not Found'},
                        status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'action': "Get Login", 'message': str(e)},
                        status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
#@permission_classes([IsAuthenticated])
def createRecruiter(request):
    if request.method=="POST":
        user=CustomUser.objects.get(id="58b383a9-f4e1-47ce-a0b1-8db5cb144f73")
        print(user)
        try:
            request.data['user']=user.id
            serializer=RecruiterSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'action': "Add New Recruiter", 'message': "Recruiter Added Successfully"},
                                status=status.HTTP_200_OK)
            else:
                return Response({'action': "Add Recruiter", 'message': serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'action': "Add Recruiter", 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['GET'])
#@permission_classes([IsAuthenticated])
def viewRecruiter(request):
    user=CustomUser.objects.get(username="Sreyas")
    # if request.user:
    #     user=request.user
    try:
        recruiter=Recruiter.objects.get(user=user)
        serializer=RecruiterSerializer(recruiter)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Recruiter.DoesNotExist:
        return Response({'error': 'Recruiter not found'}, status=status.HTTP_404_NOT_FOUND)