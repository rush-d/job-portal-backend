from django.http import Http404
from django.shortcuts import render
from rest_framework import status
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate
import requests
import json

from .models import *
from .serializers import *

ml_baseUrl='https://26bc-35-204-254-148.ngrok-free.app/'

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def CreateProfile(request):
    if request.method == 'POST':
        try:
            # Get the file data from the request
            file_data = request.FILES.get('fileInput')

            # Create the File instance and save the file data to it
            if file_data:
                file_serializer = FileSerializer(data={'uploaded_file': file_data})
                if file_serializer.is_valid():
                    file_instance = file_serializer.save()
                else:
                    return Response({'action': "Add Profile", 'message': file_serializer.errors},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                # If no file is provided, set file_instance to None
                file_instance = None

            # Create the Profile instance with other data
            profile_serializer = ProfileSerializer(data=request.data)
            if profile_serializer.is_valid():
                # Get the validated data from the serializer
                profile_data = profile_serializer.validated_data

                # Create the Profile instance and set the resume field
                profile = Profile(**profile_data, resume=file_instance)
                profile.save()
                return Response({'action': "Add Profile", 'message': "Profile Added Successfully"},
                                status=status.HTTP_201_CREATED)
            else:
                return Response({'action': "Add Profile", 'message': profile_serializer.errors},
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


@permission_classes([IsAuthenticated])
@api_view(['POST'])
def login(request):
    try:
        username = request.data['username']
        password = request.data['password']
        user = authenticate(request, username=username, password=password)

        if user:
            # User authentication succeeded
            # refresh = RefreshToken.for_user(user)
            # access_token = str(refresh.access_token)

            return Response({
                'action': "Login",
                'message': "Login Successful",
                'data': {
                    'id': user.id,
                    # 'access_token': access_token,
                    # 'refresh_token': str(refresh),  # Include the refresh token
                }
            }, status=status.HTTP_200_OK)
        else:
            # User authentication failed
            return Response({'action': "Login", 'message': "Incorrect Password"}, status=status.HTTP_401_UNAUTHORIZED)

    except Http404:
        return Response({'action': "Get Login", 'message': 'User Not Found'},
                        status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'action': "Get Login", 'message': str(e)},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createRecruiter(request):
    if request.method == "POST":
        user = request.user
        # user=CustomUser.objects.get(id="58b383a9-f4e1-47ce-a0b1-8db5cb144f73")
        try:
            request.data['user'] = user.id
            serializer = RecruiterSerializer(data=request.data)
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
@permission_classes([IsAuthenticated])
def viewRecruiter(request):
    user = request.user
    try:
        recruiter = Recruiter.objects.get(user=user)
        serializer = RecruiterViewSerializer(recruiter)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Recruiter.DoesNotExist:
        return Response({'error': 'Recruiter not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def googleLogin(request):
    try:
        username = request.data['username']
        if not CustomUser.objects.filter(username=username).exists():
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
                serializer.save()
                return Response({'action': "Add New User", 'message': "User Added Successfully"},
                                status=status.HTTP_200_OK)
            else:
                return Response({'action': "Add User", 'message': serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'action': "User Already exits", 'message': "User already exits"},
                            status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'action': "Get Login", 'message': str(e)},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def viewCandidates(request):
    try:
        profiles = Profile.objects.all()
        serializer = ProfileViewSerializer(profiles, many=True)  # Provide the queryset as data
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': 'Something went wrong'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def viewCandidateProfile(request, id):
    try:
        profile = Profile.objects.select_related('user').get(user_id=id)
        serializer = ProfileViewSerializer(profile)

        file_instance = profile.resume.uploaded_file
            
        # Define the URL of the API endpoint where you want to send the file
        api_endpoint = f'{ml_baseUrl}upload'

        # Prepare the file data as a dictionary with the file key and file object
        file = {'file': open(file_instance.path, 'rb')}
        print("ok")
        response = requests.post(api_endpoint, files=file)
        print("response: ",response.text)

        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        print("error: ",e)
        return Response({'error': 'No such candidate exists'}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def askQuery(request, id, question):
    url = f'{ml_baseUrl}ask/'

    payload = json.dumps({
        "question": question
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, data=payload)
    print("response: ",response.text)

    # Check if the request to the external API was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response content from the external API
        response_data = json.loads(response.text)
        # Return the parsed JSON response as a JSON response in your Django view
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        # If the request to the external API was not successful, return an error response
        return Response({'error': 'Failed to retrieve data from the external API'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def getUserId(request):
    print(request)
    if request.method == 'GET':
        try:
            username = request.query_params.get('username')  # Use query parameters for GET requests
            if not username:
                return Response({'error': 'Username parameter is missing'}, status=status.HTTP_400_BAD_REQUEST)

            user = CustomUser.objects.filter(
                username=username).first()  # Use filter and first() to handle user not found

            if user:
                return Response({'id': user.id, 'userType': user.user_type}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)