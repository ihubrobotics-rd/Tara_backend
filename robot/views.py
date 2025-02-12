from rest_framework.decorators import api_view,parser_classes
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
import json
import os
from django.conf import settings
from robot.models import *
from datetime import datetime
import csv
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q
from io import StringIO
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import FileSystemStorage
from urllib.parse import urljoin
from django.core.files.storage import FileSystemStorage
import zipfile
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json


#language add 
@api_view(['POST'])
def create_language(request):
    serializer = LanguageSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"status":"ok","message":"language created successfully","data":serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#language list
@api_view(['GET'])
def list_languages(request):
    languages = Language.objects.all()  
    serializer = LanguageSerializer(languages, many=True)  
    return Response({"status": "ok","message":"Languages retrieved successfully", "data": serializer.data}, status=status.HTTP_200_OK)

#language edit 
@api_view(['PUT'])
def edit_language(request, pk):
    try:
        language = Language.objects.get(pk=pk)  
    except Language.DoesNotExist:
        return Response({"status": "error", "message": "Language not found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = LanguageSerializer(language, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"status": "ok", "message": "Language updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#language detail
@api_view(['GET'])
def language_detail(request, pk):
    try:
        language = Language.objects.get(pk=pk)  
    except Language.DoesNotExist:
        return Response({"status": "error", "message": "Language not found"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = LanguageSerializer(language) 
    return Response({"status": "ok","message":"Languages retrieved successfully", "data": serializer.data}, status=status.HTTP_200_OK)

#language delete
@api_view(['DELETE'])
def delete_language(request, pk):
    try:
        language = Language.objects.get(pk=pk)  
    except Language.DoesNotExist:
        return Response({"status": "error", "message": "Language not found"}, status=status.HTTP_404_NOT_FOUND)
    
    language.delete()  
    return Response({"status": "ok", "message": "Language deleted successfully"}, status=status.HTTP_200_OK)



#add robots
@api_view(['POST'])
def create_robot(request):
    """
    Create a new robot and return the robot details along with the created timestamp.
    Also generate a JSON file with the robot's data and append new robot data to the existing file.
    """
    serializer = RobotSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        robot = serializer.save()
        serialized_data = RobotSerializer(robot, context={'request': request}).data
        robo_id = serialized_data['robo_id']  
        robot_data = {
            robo_id: {
                'id':serialized_data['id'],
                'robo_id': serialized_data['robo_id'],
                'robo_name': serialized_data['robo_name'],
                'active_status': serialized_data['active_status'],
                'battery_status': serialized_data['battery_status'],
                'working_time': serialized_data['working_time'],
                'position': serialized_data['position'],
                'language': serialized_data['language'],
                'subscription':serialized_data['subscription'],
                'current':serialized_data['current'],
                'energy':serialized_data['energy'],
                'power':serialized_data['power'],
                'voltage':serialized_data['voltage']
               
            }
        }
        filename = "robots_data.json"
        file_path = os.path.join(settings.MEDIA_ROOT, 'robots', filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as json_file:
                    try:
                        existing_data = json.load(json_file)
                    except json.JSONDecodeError:
                        existing_data = {}
            else:
                existing_data = {}

            existing_data.update(robot_data)

            with open(file_path, 'w') as json_file:
                json.dump(existing_data, json_file, indent=4)

        except IOError as e:
            return Response(
                {"status": "error", "message": f"Failed to save JSON file: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "status": "ok",
                "message": "Robot created successfully, and data saved to the JSON file.",
                "data": serialized_data,
                "json_file": filename  
            },
            status=status.HTTP_201_CREATED,
        )
    
    return Response(
        {"status": "error", "errors": serializer.errors},
        status=status.HTTP_400_BAD_REQUEST,
    )




#list robots
filename = "robots_data.json"
file_path = os.path.join(settings.MEDIA_ROOT, 'robots', filename)
@api_view(['GET'])
def list_robots(request):
    """
    List all robots from the saved JSON file and update the model if necessary.
    """
    filename = "robots_data.json"
    file_path = os.path.join(settings.MEDIA_ROOT, 'robots', filename)
    if os.path.exists(file_path):
        try:
          with open(file_path, 'r') as json_file:
                robots_data = json.load(json_file)
                
                if not isinstance(robots_data, dict):
                    return Response(
                        {"status": "error", "message": "Invalid data format in robots_data.json."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                
                for robo_id, robot_data in robots_data.items():
                    
                    if isinstance(robot_data, dict) and 'robo_id' in robot_data:
                        try:
                            robot = Robot.objects.get(robo_id=robot_data['robo_id'])
                            update_needed = False
                            
                            for field, value in robot_data.items():
                                if hasattr(robot, field):
                                    if field == 'language':  
                                        try:
                                            
                                            language_instance = Language.objects.get(language=value)
                                            setattr(robot, field, language_instance)
                                        except Language.DoesNotExist:
                                            return Response(
                                                {"status": "error", "message": f"Language '{value}' not found."},
                                                status=status.HTTP_400_BAD_REQUEST,
                                            )
                                    else:
                                        
                                        if getattr(robot, field) != value:
                                            setattr(robot, field, value)
                                            update_needed = True
                            
                            if update_needed:
                                robot.save()
                        except Robot.DoesNotExist:
                            continue  

                return Response(
                    {
                        "status": "ok",
                        "message": "Robots data retrieved and model updated if necessary.",
                        "data": robots_data
                    },
                    status=status.HTTP_200_OK,
                )
        
        except json.JSONDecodeError:
            return Response(
                {"status": "error", "message": "Failed to decode JSON data."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    return Response(
        {"status": "error", "message": "No robots data found."},
        status=status.HTTP_404_NOT_FOUND,
    )


#passing json files api
@api_view(['GET'])
def get_robots_file(request):
    """
    Share the robots_data.json file.
    """
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as json_file:
                robots_data = json.load(json_file)
            return Response({"status": "ok", "data": robots_data}, status=status.HTTP_200_OK)
        except json.JSONDecodeError:
            return Response({"status": "error", "message": "Failed to decode JSON."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({"status": "error", "message": "File not found."}, status=status.HTTP_404_NOT_FOUND)

#manually updation api
@api_view(['POST'])
def update_robots_file(request):
    """
    Update the robots_data.json file and the corresponding Robot database entry.
    """
    try:
        filename = "robots_data.json"
        file_path = os.path.join(settings.MEDIA_ROOT, 'robots', filename)
        robots_data = request.data  # Expecting JSON format: { "robo_id": { "field": "value", ... } }

        if not robots_data:
            return Response({"status": "error", "message": "No data provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Load existing JSON data
        if os.path.exists(file_path):
            with open(file_path, 'r') as json_file:
                try:
                    existing_data = json.load(json_file)
                except json.JSONDecodeError:
                    existing_data = {}
        else:
            existing_data = {}

        if not isinstance(existing_data, dict):
            existing_data = {}

        updated_data = {}

        for robo_id, updated_fields in robots_data.items():
            if robo_id not in existing_data:
                return Response(
                    {"status": "error", "message": f"Robot ID {robo_id} does not exist in JSON file."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Update JSON file
            existing_data[robo_id].update(updated_fields)
            updated_data[robo_id] = existing_data[robo_id]

            # Update Database (if fields match Robot model)
            try:
                robot = Robot.objects.get(robo_id=robo_id)
                for field, value in updated_fields.items():
                    if hasattr(robot, field):
                        # Check if the field is language and fetch the corresponding Language object
                        if field == 'language':
                            language_instance = Language.objects.filter(language=value).first()
                            if language_instance:
                                setattr(robot, field, language_instance)
                            else:
                                return Response(
                                    {"status": "error", "message": f"Language '{value}' not found."},
                                    status=status.HTTP_404_NOT_FOUND
                                )
                        else:
                            setattr(robot, field, value)
                robot.save()
            except Robot.DoesNotExist:
                return Response(
                    {"status": "error", "message": f"Robot ID {robo_id} not found in database."},
                    status=status.HTTP_404_NOT_FOUND
                )

        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Save updated JSON data
        with open(file_path, 'w') as json_file:
            json.dump(existing_data, json_file, indent=4)

        return Response(
            {"status": "ok", "message": "Robot data updated successfully in JSON file and database.", "data": updated_data},
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {"status": "error", "message": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
#robot details update 

@api_view(['PUT'])
def update_robot_by_id(request, robo_id):
    """
    Update an existing robot using robo_id and update the robots_data.json file.
    """
    try:
        robot = Robot.objects.get(robo_id=robo_id)
    except Robot.DoesNotExist:
        return Response(
            {"status": "error", "message": f"Robot with robo_id {robo_id} not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    request_data = request.data.copy()

    # Convert and validate language field
    if 'language' in request_data:
        try:
            language_id = int(request_data['language'])  # Convert to integer
            language_instance = get_object_or_404(Language, id=language_id)
            request_data['id'] = language_instance  # Assign the Language instance, not just the ID
        except (ValueError, Language.DoesNotExist):
            return Response(
                {"status": "error", "message": "Invalid language ID."},
                status=status.HTTP_400_BAD_REQUEST,
            )


    # Serialize and update the robot instance
    serializer = RobotSerializer(robot, data=request_data, partial=True, context={'request': request})

    if serializer.is_valid():
        robot = serializer.save()
        serialized_data = RobotSerializer(robot, context={'request': request}).data
        robo_id = serialized_data['robo_id']

        # Load existing data from robots_data.json
        filename = "robots_data.json"
        file_path = os.path.join(settings.MEDIA_ROOT, 'robots', filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as json_file:
                    try:
                        existing_data = json.load(json_file)
                    except json.JSONDecodeError:
                        existing_data = {}
            else:
                existing_data = {}

            # Update the robot data in the JSON file
            if robo_id in existing_data:
                existing_data[robo_id].update({
                    'robo_name': serialized_data['robo_name'],
                    'active_status': serialized_data['active_status'],
                    'battery_status': serialized_data['battery_status'],
                    'working_time': serialized_data['working_time'],
                    'position': serialized_data['position'],
                    'language': serialized_data['language'],
                    'subscription': serialized_data['subscription']
                })

            with open(file_path, 'w') as json_file:
                json.dump(existing_data, json_file, indent=4)

        except IOError as e:
            return Response(
                {"status": "error", "message": f"Failed to update JSON file: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "status": "ok",
                "message": "Robot updated successfully, and data saved to the JSON file.",
                "data": serialized_data,
                "json_file": filename
            },
            status=status.HTTP_200_OK,
        )

    return Response(
        {"status": "error", "errors": serializer.errors},
        status=status.HTTP_400_BAD_REQUEST,
    )

#delete robot
@api_view(['DELETE'])
def delete_robot(request, robo_id):
    """
    Delete a robot by robo_id and update the robots_data.json file.
    """
    try:
        robot = Robot.objects.get(robo_id=robo_id)
    except Robot.DoesNotExist:
        return Response(
            {"status": "error", "message": f"Robot with robo_id {robo_id} not found."},
            status=status.HTTP_404_NOT_FOUND,
        )
    
    robot.delete()
    filename = "robots_data.json"
    file_path = os.path.join(settings.MEDIA_ROOT, 'robots', filename)
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as json_file:
                try:
                    existing_data = json.load(json_file)
                    if not isinstance(existing_data, dict):
                        raise ValueError("Data in JSON file is not in the expected format (dict).")
                except json.JSONDecodeError:
                    existing_data = {}  
        except IOError as e:
            return Response(
                {"status": "error", "message": f"Failed to read JSON file: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        if robo_id in existing_data:
            del existing_data[robo_id]
        else:
            return Response(
                {"status": "error", "message": f"Robot with robo_id {robo_id} not found in the JSON file."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            with open(file_path, 'w') as json_file:
                json.dump(existing_data, json_file, indent=4)
        except IOError as e:
            return Response(
                {"status": "error", "message": f"Failed to save JSON file: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    return Response(
        {"status": "ok", "message": f"Robot with robo_id {robo_id} deleted successfully."},
        status=status.HTTP_200_OK,
    )



@api_view(['GET'])
def robot_detail(request, robo_id):
    """
    Retrieve the details of a robot using the robo_id.
    """
    # First, try to get the robot data from the database (if available)
    try:
        robot = Robot.objects.get(robo_id=robo_id)
        serialized_data = RobotSerializer(robot).data
        
        # Ensure the image field is returned as an absolute URL
        if serialized_data.get('image'):
            serialized_data['image'] = request.build_absolute_uri(serialized_data['image'])
        
        return Response(
            {"status": "ok", "data": serialized_data},
            status=status.HTTP_200_OK
        )
    except Robot.DoesNotExist:
        # If not found in the database, try reading from the JSON file
        filename = "robots_data.json"
        file_path = os.path.join(settings.MEDIA_ROOT, 'robots', filename)

        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as json_file:
                    existing_data = json.load(json_file)
                    if str(robo_id) in existing_data:
                        robot_data = existing_data[str(robo_id)]
                        
                        # If there's an image in the JSON data, make it an absolute URL
                        if robot_data.get('image'):
                            robot_data['image'] = request.build_absolute_uri(robot_data['image'])
                        
                        return Response(
                            {"status": "ok", "data": robot_data},
                            status=status.HTTP_200_OK
                        )
                    else:
                        return Response(
                            {"status": "error", "message": "Robot not found in the JSON data"},
                            status=status.HTTP_404_NOT_FOUND
                        )
            except json.JSONDecodeError:
                return Response(
                    {"status": "error", "message": "Failed to decode JSON file"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            return Response(
                {"status": "error", "message": "Robot not found"},
                status=status.HTTP_404_NOT_FOUND
            )

#sale robots
@api_view(['POST'])
def create_purchase_robot(request):
    """
    Create a PurchaseRobot instance, update the robot subscription to True,
    and update the robots_data.json file with the correct format.
    """
    serializer = PurchaseRobotSerializer(data=request.data)
    if serializer.is_valid():
        purchase_robot = serializer.save()
        robot = purchase_robot.robot
        if not robot.subscription:
            robot.subscription = True
            robot.save()
        serialized_data = PurchaseRobotSerializer(purchase_robot).data
        robo_id = serialized_data['robot']['robo_id']
        robot_data = {
            robo_id: {
                'id':serialized_data['robot']['id'],
                'robo_id': serialized_data['robot']['robo_id'],
                'robo_name': serialized_data['robot']['robo_name'],
                'active_status': serialized_data['robot']['active_status'],
                'subscription': robot.subscription,  
                'battery_status': serialized_data['robot']['battery_status'],
                'working_time': serialized_data['robot']['working_time'],
                'position': serialized_data['robot']['position'],
                'language': serialized_data['robot']['language'],
                'last_updated': datetime.now().isoformat()  
            }
        }

        filename = "robots_data.json"
        file_path = os.path.join(settings.MEDIA_ROOT, 'robots', filename)

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as json_file:
                    try:
                        existing_data = json.load(json_file)
                    except json.JSONDecodeError:
                        existing_data = {}
            else:
                existing_data = {}
            existing_data.update(robot_data)
            with open(file_path, 'w') as json_file:
                json.dump(existing_data, json_file, indent=4)

        except IOError as e:
            return Response(
                {"status": "error", "message": f"Failed to save JSON file: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "status": "ok",
                "message": "PurchaseRobot created successfully, robot subscription updated, and JSON file updated.",
                "data": serialized_data,
                "json_file": filename  
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(
        {"status": "error", "errors": serializer.errors},
        status=status.HTTP_400_BAD_REQUEST,
    )




#purchase robot list
@api_view(['GET'])
def list_purchase_robots(request):
    """
    List all PurchaseRobot records with full details of the robot and user.
    """
    purchase_robots = PurchaseRobot.objects.all() 
    serializer = PurchaseRobotSerializer(purchase_robots, many=True)  
    return Response({
        "status": "ok",
        "message": "PurchaseRobot list retrieved successfully.",
        "data": serializer.data
    }, status=status.HTTP_200_OK)


#purchase robot update
@api_view(['PUT'])
def update_purchase_robot(request, pk):
    """
    Update an existing PurchaseRobot instance, update the robot subscription,
    and update the robots_data.json file with the correct format.
    """
    try:
       purchase_robot = PurchaseRobot.objects.get(pk=pk)
    except PurchaseRobot.DoesNotExist:
        return Response(
            {"status": "error", "message": "PurchaseRobot not found."},
            status=status.HTTP_404_NOT_FOUND,
        )
    serializer = PurchaseRobotSerializer(purchase_robot, data=request.data, partial=True)
    
    if serializer.is_valid():
        purchase_robot = serializer.save()
        robot = purchase_robot.robot

        if not robot.subscription:
            robot.subscription = True
            robot.save()

        serialized_data = PurchaseRobotSerializer(purchase_robot).data
        robo_id = serialized_data['robot']['robo_id']
        
        robot_data = {
            robo_id: {
                'robo_id': serialized_data['robot']['robo_id'],
                'robo_name': serialized_data['robot']['robo_name'],
                'active_status': serialized_data['robot']['active_status'],
                'subscription': robot.subscription,  
                'battery_status': serialized_data['robot']['battery_status'],
                'working_time': serialized_data['robot']['working_time'],
                'position': serialized_data['robot']['position'],
                'language': serialized_data['robot']['language'],
                'last_updated': datetime.now().isoformat()  
            }
        }

        filename = "robots_data.json"
        file_path = os.path.join(settings.MEDIA_ROOT, 'robots', filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as json_file:
                    try:
                        existing_data = json.load(json_file)
                    except json.JSONDecodeError:
                        existing_data = {}
            else:
                existing_data = {}

            existing_data.update(robot_data)

            with open(file_path, 'w') as json_file:
                json.dump(existing_data, json_file, indent=4)

        except IOError as e:
            return Response(
                {"status": "error", "message": f"Failed to save JSON file: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "status": "ok",
                "message": "PurchaseRobot updated successfully, robot subscription updated, and JSON file updated.",
                "data": serialized_data,
                "json_file": filename  
            },
            status=status.HTTP_200_OK,
        )

    return Response(
        {"status": "error", "errors": serializer.errors},
        status=status.HTTP_400_BAD_REQUEST,
    )

#delete purchase robot
@api_view(['DELETE'])
def delete_purchase_robot(request, pk):
    """
    Delete a PurchaseRobot instance, set the corresponding robot subscription to False,
    and update the robots_data.json file by changing the subscription status.
    """
    try:
        purchase_robot = PurchaseRobot.objects.get(pk=pk)
    except PurchaseRobot.DoesNotExist:
        return Response(
            {"status": "error", "message": "PurchaseRobot not found."},
            status=status.HTTP_404_NOT_FOUND,
        )
    robot = purchase_robot.robot
    robot.subscription = False
    robot.save()
    serialized_data = PurchaseRobotSerializer(purchase_robot).data
    robo_id = serialized_data['robot']['robo_id']

    filename = "robots_data.json"
    file_path = os.path.join(settings.MEDIA_ROOT, 'robots', filename)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as json_file:
                try:
                    existing_data = json.load(json_file)
                except json.JSONDecodeError:
                    existing_data = {}
        else:
            existing_data = {}
        if robo_id in existing_data:
            
            existing_data[robo_id]['subscription'] = False
            existing_data[robo_id]['last_updated'] = datetime.now().isoformat()  
            
            with open(file_path, 'w') as json_file:
                json.dump(existing_data, json_file, indent=4)
        else:
            return Response(
                {"status": "error", "message": "Robot data not found in JSON file."},
                status=status.HTTP_404_NOT_FOUND,
            )

    except IOError as e:
        return Response(
            {"status": "error", "message": f"Failed to update JSON file: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    purchase_robot.delete()

    return Response(
        {
            "status": "ok",
            "message": "PurchaseRobot deleted successfully, robot subscription set to False, and JSON file updated.",
            "data": {"robo_id": robo_id},
            "json_file": filename 
        },
        status=status.HTTP_200_OK,
    )

#list user robots
@api_view(['GET'])
def list_purchase_robot_by_user(request, user_id):
    """
    List all PurchaseRobot instances for a specific user.
    """
    try:
        purchase_robots = PurchaseRobot.objects.filter(user__id=user_id)
        
        serializer = PurchaseRobotSerializer(purchase_robots, many=True)
        
        return Response(
            {"status": "ok", "data": serializer.data},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response(
            {"status": "error", "message": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    

#customer create
@api_view(['POST'])
def create_new_customer(request):
    """
    Create a new NewCustomers instance and associate it with a Robot using robo_id.
    """
    robo_id = request.data.get('robo_id') 
    robot = get_object_or_404(Robot, robo_id=robo_id)
    serializer = NewCustomersSerializer(data=request.data)
    if serializer.is_valid():
        new_customer = serializer.save(robot=robot)
        response_data = serializer.data
        response_data['robot'] = {
            "id": robot.id,
            "robo_name": robot.robo_name,
            "robo_id": robot.robo_id,
            "active_status": robot.active_status,
            "subscription": robot.subscription,
            "battery_status": robot.battery_status,
            "working_time": robot.working_time,
            "position": robot.position,
        }
        return Response(
            {"status": "ok", "message": "New customer created successfully", "data": response_data},
            status=status.HTTP_201_CREATED
        )
    
    return Response(
        {"status": "error", "errors": serializer.errors},
        status=status.HTTP_400_BAD_REQUEST
    )


#list customers
@api_view(['GET'])
def list_new_customers(request):
    """
    List all NewCustomers instances.
    """
    customers = NewCustomers.objects.all()
    serializer = NewCustomersSerializer(customers, many=True)
    return Response(
        {"status": "ok", "message": "New customers retrieved successfully", "data": serializer.data},
        status=status.HTTP_200_OK
    )


# download csv
@api_view(['GET'])
def download_customers_csv(request):
    """
    Generate a CSV file of NewCustomers data with robot ID and provide it for download.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="new_customers.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Username', 'Session ID', 'Gender', 'Timestamp', 'Purpose', 'Robot ID'])
    customers = NewCustomers.objects.all()
    for customer in customers:
        robot_id = customer.robot.robo_id if customer.robot else None
        writer.writerow([
            customer.id,
            customer.username,
            customer.session_id,
            customer.gender,
            customer.time_stamp,
            customer.purpose,
            robot_id 
        ])
    
    return response


#summery edit view
@api_view(['PATCH'])
def edit_customer_summery(request, session_id):
    """
    Edit the 'summery' field of an existing NewCustomers instance using session_id from the URL
    and return all customer data for frontend use.
    """
    try:
        customer = NewCustomers.objects.get(session_id=session_id)
    except NewCustomers.DoesNotExist:
        return Response(
            {"status": "error", "message": "Customer with the provided session ID does not exist."},
            status=status.HTTP_404_NOT_FOUND
        )
    
    summery = request.data.get('summery')
    if summery is not None:
        customer.summery = summery
        customer.save()

    serializer = NewCustomersSerializer(customer)
    return Response(
        {
            "status": "ok",
            "message": "Customer data retrieved successfully." if summery is None else "Summery updated successfully.",
            "data": serializer.data  
        },
        status=status.HTTP_200_OK
    )


#customer detail view 
@api_view(['GET'])
def customer_detail_view(request, session_id):
    """
    Retrieve detailed information of a NewCustomers instance using session_id.
    """
    # Retrieve the NewCustomers instance
    try:
        customer = NewCustomers.objects.get(session_id=session_id)
    except NewCustomers.DoesNotExist:
        return Response(
            {"status": "error", "message": "Customer with the provided session ID does not exist."},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Serialize the customer data
    serializer = NewCustomersSerializer(customer)
    return Response(
        {
            "status": "ok",
            "message": "Customer details retrieved successfully.",
            "data": serializer.data
        },
        status=status.HTTP_200_OK
    )

#employee create
@api_view(['POST'])
def create_employee(request):
    """
    Create a new employee and return the employee details.
    """
    serializer = EmployeeSerializer(data=request.data)
    if serializer.is_valid():
        employee = serializer.save()  
        serialized_data = EmployeeSerializer(employee).data 
        return Response(
            {
                "status": "ok",
                "message": "Employee created successfully.",
                "data": serialized_data,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(
        {
            "status": "error",
            "errors": serializer.errors,
        },
        status=status.HTTP_400_BAD_REQUEST,
    )

#employee list
@api_view(['GET'])
def list_employees(request):
    """
    Retrieve a list of all employees.
    """
    employees = Employee.objects.all() 
    serialized_data = EmployeeSerializer(employees, many=True).data  
    return Response(
        {
            "status": "ok",
            "message": "Employee list retrieved successfully.",
            "data": serialized_data,
        },
        status=status.HTTP_200_OK,
    )


#employee edit
@api_view(['PUT'])
def edit_employee(request, employee_id):
    """
    Edit an existing employee's details by employee_id.
    """
    try:
        employee = Employee.objects.get(employee_id=employee_id)  
    except Employee.DoesNotExist:
        return Response(
            {"status": "error", "message": "Employee not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = EmployeeSerializer(employee, data=request.data, partial=True)  
    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                "status": "ok",
                "message": "Employee updated successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    return Response(
        {
            "status": "error",
            "errors": serializer.errors,
        },
        status=status.HTTP_400_BAD_REQUEST,
    )

#employee detail
@api_view(['GET'])
def employee_detail(request, employee_id):
    """
    Retrieve details of an employee by employee_id.
    """
    try:
        employee = Employee.objects.get(employee_id=employee_id)  
    except Employee.DoesNotExist:
        return Response(
            {"status": "error", "message": "Employee not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = EmployeeSerializer(employee)
    return Response(
        {
            "status": "ok",
            "message": "Employee details retrieved successfully.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )

#delete employee
@api_view(['DELETE'])
def delete_employee(request, employee_id):
    """
    Delete an employee by employee_id.
    """
    try:
        employee = Employee.objects.get(employee_id=employee_id)  
        employee.delete() 
        return Response(
            {"status": "ok", "message": "Employee deleted successfully."},
            status=status.HTTP_200_OK,
        )
    except Employee.DoesNotExist:
        return Response(
            {"status": "error", "message": "Employee not found."},
            status=status.HTTP_404_NOT_FOUND,
        )
    
#add punching
@api_view(['POST'])
def create_punch(request):
    """
    Create a punch record using employee_id.
    Ensure an employee can punch in only once per day.
    """
    employee_id = request.data.get('employee_id')
    date_str = request.data.get('date')

    if not employee_id or not date_str:
        return Response(
            {"status": "error", "message": "Employee ID and Date are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        employee = Employee.objects.get(employee_id=employee_id)
    except Employee.DoesNotExist:
        return Response(
            {"status": "error", "message": "Employee not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return Response(
            {"status": "error", "message": "Invalid date format. Use YYYY-MM-DD."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check if a punch record already exists for the same employee on the same date
    if Punch.objects.filter(employee=employee, date=date).exists():
        return Response(
            {"status": "error", "message": "Punch-in record already exists for this date."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    punch_data = {
        "employee": employee.id,
        "date": date_str,
        "punch_in": request.data.get('punch_in'),
        "punch_out": request.data.get('punch_out'),
    }

    serializer = PunchSerializer(data=punch_data)
    if serializer.is_valid():
        punch = serializer.save()
        punch_data = PunchSerializer(punch).data
        employee_data = EmployeeSerializer(employee).data

        return Response(
            {
                "status": "ok",
                "message": "Punch created successfully.",
                "data": {
                    "punch": punch_data,
                    "employee": employee_data,
                },
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(
        {"status": "error", "errors": serializer.errors},
        status=status.HTTP_400_BAD_REQUEST,
    )

#delete punch in    
@api_view(['DELETE'])
def delete_punch(request, punch_id):
    """
    Delete a punch record by ID.
    """
    try:
        punch = Punch.objects.get(id=punch_id)
        punch.delete()
        return Response(
            {"status": "ok", "message": "Punch record deleted successfully."},
            status=status.HTTP_200_OK,
        )
    except Punch.DoesNotExist:
        return Response(
            {"status": "error", "message": "Punch record not found."},
            status=status.HTTP_404_NOT_FOUND,
        )




#list punching
@api_view(['GET'])
def list_punches(request):
    """
    List all punch records with employee details.
    Supports filtering by date, employee_id, or both.
    """
    date_filter = request.query_params.get('date', None)
    employee_id_filter = request.query_params.get('employee_id', None)
    punches = Punch.objects.all()
    if date_filter:
        try:
            punches = punches.filter(date=date_filter)  
        except ValueError:
            return Response({
                "status": "error",
                "message": "Invalid date format. Use 'YYYY-MM-DD'."
            }, status=status.HTTP_400_BAD_REQUEST)
    if employee_id_filter:
        punches = punches.filter(employee__employee_id=employee_id_filter) 
    result = []
    for punch in punches:
        punch_data = PunchSerializer(punch).data
        employee_data = EmployeeSerializer(punch.employee).data
        result.append({
            "punch": punch_data,
            "employee": employee_data,
        })

    return Response({
        "status": "ok",
        "message": "Punch records retrieved successfully.",
        "data": result,
    })

#download csv
@api_view(['GET'])
def download_csv(request):
    """
    List all punch records with employee details.
    Supports filtering by date, employee_id, or both.
    Allows CSV export.
    """
    date_filter = request.query_params.get('date', None)
    employee_id_filter = request.query_params.get('employee_id', None)
    punches = Punch.objects.all()
    if date_filter:
        try:
            datetime.strptime(date_filter, "%Y-%m-%d")  
            punches = punches.filter(date=date_filter)  
        except ValueError:
            return Response({
                "status": "error",
                "message": "Invalid date format. Use 'YYYY-MM-DD'."
            }, status=status.HTTP_400_BAD_REQUEST)
    if employee_id_filter:
        punches = punches.filter(employee__employee_id=employee_id_filter)
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Punch ID', 'Employee ID', 'Employee Name', 'Designation', 'Date', 'Punch In', 'Punch Out'])
    for punch in punches:
        if punch.employee:
            employee = punch.employee
            writer.writerow([
                punch.id,
                employee.employee_id,
                employee.employee_name,
                employee.designation,
                punch.date,
                punch.punch_in,
                punch.punch_out,
            ])
        else:
            writer.writerow([
                punch.id,
                'N/A',  
                'N/A',  
                'N/A', 
                punch.date,
                punch.punch_in,
                punch.punch_out,
            ])
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="punch_records.csv"'
    return response



@api_view(['PUT'])
def edit_punch_out(request, employee_id):
    """
    Edit the punch record's punch_out using employee_id.
    If date is not provided, the current date is used.
    """
    # Validate employee_id
    if not employee_id:
        return Response(
            {"status": "error", "message": "Employee ID is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    # Check if the employee exists
    try:
        employee = Employee.objects.get(employee_id=employee_id)
    except Employee.DoesNotExist:
        return Response(
            {"status": "error", "message": "Employee not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Get date from request or use the current date
    date = request.data.get('date')
    if not date:
        provided_date = datetime.now().date()  # Use the current date if not provided
    else:
        # Parse and validate the provided date
        try:
            provided_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"status": "error", "message": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    # Find the punch record with matching employee and date
    try:
        punch = Punch.objects.get(employee=employee, date=provided_date)
    except Punch.DoesNotExist:
        return Response(
            {"status": "error", "message": "Punch record not found for the given employee and date."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Validate punch_out from request
    punch_out = request.data.get('punch_out')
    if not punch_out:
        return Response(
            {"status": "error", "message": "Punch out time is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Update punch_out field
    punch.punch_out = punch_out
    punch.save()

    # Serialize the updated punch record
    punch_data = PunchSerializer(punch).data

    return Response(
        {
            "status": "ok",
            "message": "Punch out time updated successfully.",
            "data": punch_data,
        },
        status=status.HTTP_200_OK,
    )



@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_robot_pdf(request, robo_id):
    """
    Upload a PDF file for the specified `robo_id`.
    Remove all existing PDFs in the 'PDF/<robo_id>' directory before saving the new file.
    """
    pdf_file = request.FILES.get('pdf_file')
    if not pdf_file or not pdf_file.name.endswith('.pdf'):
        return Response(
            {"status": "error", "message": "A valid PDF file is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    directory_path = os.path.join(settings.MEDIA_ROOT, 'PDF', robo_id)
    os.makedirs(directory_path, exist_ok=True)

    try:
      
        for existing_file in os.listdir(directory_path):
            if existing_file.endswith('.pdf'):
                os.remove(os.path.join(directory_path, existing_file))
        file_storage = FileSystemStorage(location=directory_path)
        file_storage.save(pdf_file.name, pdf_file)

    except Exception as e:
        return Response(
            {"status": "error", "message": f"Failed to upload PDF: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    relative_file_url = os.path.join(settings.MEDIA_URL, 'PDF', robo_id, pdf_file.name)
    relative_file_url = relative_file_url.replace('\\', '/') 
    absolute_file_url = request.build_absolute_uri(relative_file_url)

    return Response(
        {
            "status": "ok",
            "message": "PDF uploaded successfully. All previous PDFs were removed.",
            "file_url": absolute_file_url,
        },
        status=status.HTTP_201_CREATED,
    )

@api_view(['GET'])
def get_robot_pdf_details(request, robo_id):
    """
    Retrieve details of the uploaded PDF for the specified `robo_id`.
    Returns the file URL if the PDF exists.
    """
    directory_path = os.path.join(settings.MEDIA_ROOT, 'PDF', robo_id)
    if not os.path.exists(directory_path):
        return Response(
            {"status": "error", "message": "No PDF directory found for the given robo_id."},
            status=status.HTTP_404_NOT_FOUND,
        )
    pdf_files = [f for f in os.listdir(directory_path) if f.endswith('.pdf')]
    if not pdf_files:
        return Response(
            {"status": "error", "message": "No PDF found for the given robo_id."},
            status=status.HTTP_404_NOT_FOUND,
        )
    pdf_file = pdf_files[0]
    relative_file_url = os.path.join(settings.MEDIA_URL, 'PDF', robo_id, pdf_file)
    relative_file_url = relative_file_url.replace('\\', '/') 
    absolute_file_url = request.build_absolute_uri(relative_file_url)

    return Response(
        {
            "status": "ok",
            "message": "PDF details retrieved successfully.",
            "file_name": pdf_file,
            "file_url": absolute_file_url,
        },
        status=status.HTTP_200_OK,
    )


# zip uploads 
@login_required
def upload_zip_file(request):
    if request.method == 'POST':
        robot_id = request.POST.get('robot')  
        zip_file = request.FILES.get('zip_file')
        if not robot_id or not zip_file:
            return render(request, 'upload.html', {'error': 'Robot and ZIP file are required!', 'robots': Robot.objects.all()})

        try:
            robot = Robot.objects.get(id=robot_id) 
        except Robot.DoesNotExist:
            return render(request, 'upload.html', {'error': 'Invalid robot selection.', 'robots': Robot.objects.all()})

        robo_folder_name = robot.robo_id  
        if not zip_file.name.endswith('.zip'):
            return render(request, 'upload.html', {'error': 'Only ZIP files are allowed.', 'robots': Robot.objects.all()})

        upload_dir = os.path.join(settings.MEDIA_ROOT, 'robot_files', robo_folder_name)
        if os.path.exists(upload_dir):
            for file in os.listdir(upload_dir):
                file_path = os.path.join(upload_dir, file)
                if os.path.isfile(file_path) and file.endswith('.zip'):
                    os.remove(file_path)  
        else:
            os.makedirs(upload_dir, exist_ok=True)
        fs = FileSystemStorage(location=upload_dir)
        zip_filename = fs.save(zip_file.name, zip_file)
        robot_file = RobotFile(robot=robot, zip_file=f'robot_files/{robo_folder_name}/{zip_filename}')
        robot_file.save()
        return render(request, 'upload.html', {'success': 'ZIP file uploaded successfully!', 'robots': Robot.objects.all()})
    return render(request, 'upload.html', {'robots': Robot.objects.all()})

#get zip file path
@api_view(['GET'])
def list_zip_files(request, robo_id):
    try:
        robot = Robot.objects.get(robo_id=robo_id)  
    except Robot.DoesNotExist:
        return Response({"error": "Robot with given robo_id not found"}, status=404)
    robot_files = RobotFile.objects.filter(robot=robot).order_by('-uploaded_at')

    if not robot_files:
        return Response({"error": "No files found for this robot"}, status=404)
    latest_file = robot_files.first()
    zip_file_url = request.build_absolute_uri(latest_file.zip_file.url)
    file_data = {
        "zip_file_url": zip_file_url, 
        "robot_name": latest_file.robot.robo_name,  
        "uploaded_at": latest_file.uploaded_at  
    }

    return Response(file_data)





# video playing updation
state = {
    "listening": False,
    "stand_by": False,
    "speaking": False,
}

# Mapping of commands to state keys
COMMAND_MAPPING = {
    "SPEAKING_VIDEO": "speaking",
    "LISTENING_VIDEO": "listening",
    "STAND_BY_VIDEO": "stand_by",
}

@api_view(["POST"])
def update_status(request):
    """
    API to update the status based on command input.
    Only one key can be True at a time.
    """
    data = request.data
    command = data.get("command")  
    if not command:
        return Response({"message": "No command provided", "command": None, "data": state}, status=status.HTTP_200_OK)

    if command not in COMMAND_MAPPING:
        return Response({"error": "Invalid command provided", "command": command}, status=status.HTTP_400_BAD_REQUEST)
    key_to_update = COMMAND_MAPPING[command]
    for key in state:
        state[key] = False
    state[key_to_update] = True
    return Response({
        "status": "OK",
        "command": command,
        key_to_update: True
    }, status=status.HTTP_200_OK)

@api_view(["GET"])
def list_status(request):
    """
    API to return the current state of all statuses.
    """
    return Response(
        {
            "status": "OK",
            "data": state,
        },
        status=status.HTTP_200_OK,
    )