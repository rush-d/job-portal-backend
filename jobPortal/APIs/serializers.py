from rest_framework import serializers
from rest_framework import serializers

from .models import *

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model=File
        fields=['uploaded_file']
    
    def __str__(self):
        return self.uploaded_file.name

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ['last_login_time','id']

    def __str__(self):
        return self.user.username
    
class ProfileViewSerializer(serializers.ModelSerializer):
    resume = FileSerializer()
    class Meta:
        model=Profile
        fields='__all__'

    def __str__(self):
            return self.user.username

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields=['username','password','user_type']

    def __str__(self):
        return self.username
    
class RecruiterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recruiter
        fields='__all__'

    def __str__(self):
        return self.company
