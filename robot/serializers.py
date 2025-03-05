from rest_framework import serializers
from robot.models import *
import random
import string
from accounts.serilaizers import *



class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model=Language
        fields = '__all__' 


class RobotSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    language = serializers.CharField(required=False)

    class Meta:
        model = Robot
        fields = ['id', 'robo_name', 'robo_id', 'active_status', 
                  'battery_status', 'working_time', 'position', 
                  'created_at', 'subscription', 'language', 'image','voltage','current','voltage','power','energy','quality','map']
        extra_kwargs = {
            'robo_id': {'required': True},
            'image': {'required': False},  # Ensure image is optional
        }

    def create(self, validated_data):
        language_name = validated_data.pop('language', None)
        robot = Robot.objects.create(**validated_data)

        if language_name:
            language, created = Language.objects.get_or_create(language=language_name)
            robot.language = language
            robot.save()

        return robot


class PurchaseRobotSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseRobot
        fields = ['id','robot', 'user', 'date', 'end_date', 'maintenance_hours']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['robot'] = RobotSerializer(instance.robot).data
        representation['user'] = CustomUserSerializer(instance.user).data
        return representation


class NewCustomersSerializer(serializers.ModelSerializer):
    robot = RobotSerializer(read_only=True)
    class Meta:
        model = NewCustomers
        fields = ['id', 'username', 'session_id', 'gender', 'time_stamp', 'purpose','robot','summery']

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model=Employee
        fields=['id','employee_id','employee_name','designation']

class PunchSerializer(serializers.ModelSerializer):
    employee = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all())
    class Meta:
        model = Punch
        fields = ['id', 'employee', 'date', 'punch_in', 'punch_out']


class RobotFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RobotFile
        fields = ['robot', 'zip_file', 'uploaded_at']

