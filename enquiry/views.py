from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Enquiry
from .serializers import *
from django.shortcuts import get_object_or_404
from django.core.cache import cache
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.http import JsonResponse

# enquiry logo create
@api_view(['POST'])
def create_enquiry(request):
    """Allow enquiry creation where:
    - Admin can manually select `user_id`
    - Users automatically get their `user_id`
    """
    user = request.user if request.user.is_authenticated else None
    data = request.data.copy()
    if user:
        if user.role == "admin":
            user_id = data.get("user")  
            if not user_id:
                return Response({"error": "Admin must select a user."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user_id = user.id
            data["user"] = user_id  

    serializer = EnquirySerializer(data=data, context={'request': request})
    if serializer.is_valid():
        serializer.save()  
        return Response({"status": "ok", "message": "Enquiry created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# enquiry logo list
@api_view(['GET'])
def list_enquiries(request):
    """
    List enquiries:
    - Admins see all enquiries
    - Users see only their own enquiries
    - If no user is specified, show all enquiries (public access)
    """

    user_id = request.GET.get("user_id")  

    if user_id:
        enquiries = Enquiry.objects.filter(user_id=user_id)  
    else:
        enquiries = Enquiry.objects.all() 

    serializer = EnquirySerializer(enquiries, many=True, context={'request': request})
    return Response({"status":"ok","message":"Data retrieved successfully","data":serializer.data}, status=status.HTTP_200_OK)


# enquiry logo edit 
@api_view(['PUT'])
def edit_enquiry(request, enquiry_id):
    """
    Edit an enquiry:
    - Admins can update any enquiry
    - Users can update only their own enquiries
    - Requires `user_id` in the request body
    """
    try:
        enquiry = Enquiry.objects.get(id=enquiry_id)
    except Enquiry.DoesNotExist:
        return Response({"error": "Enquiry not found"}, status=status.HTTP_404_NOT_FOUND)

    data = request.data.copy()
    user_id = data.get("user")  

    if not user_id:
        return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    
    if enquiry.user.id != int(user_id):
        return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

    serializer = EnquirySerializer(enquiry, data=data, partial=True, context={'request': request})

    if serializer.is_valid():
        serializer.save()
        return Response({"status": "ok", "message": "Enquiry updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# enquiry logo detail 
@api_view(['GET'])
def enquiry_detail(request, enquiry_id):
    """Retrieve a single enquiry by ID."""
    try:
        enquiry = Enquiry.objects.get(id=enquiry_id)
    except Enquiry.DoesNotExist:
        return Response({"error": "Enquiry not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = EnquirySerializer(enquiry, context={'request': request})
    return Response({"status":"ok","message":"Data retrieved successfully","data":serializer.data}, status=status.HTTP_200_OK)

# enquiry logo delete
@api_view(['DELETE'])
def delete_enquiry(request, enquiry_id):
    """Delete an enquiry by ID."""
    try:
        enquiry = Enquiry.objects.get(id=enquiry_id)
        enquiry.delete()
        return Response({"status": "ok", "message": "Enquiry deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except Enquiry.DoesNotExist:
        return Response({"error": "Enquiry not found"}, status=status.HTTP_404_NOT_FOUND)



@api_view(['POST'])
def create_subbutton(request):
    """
    Create a new SubButton entry:
    - Requires `enquiry` (ID of an existing enquiry)
    - Requires `subheading`
    """
    serializer = SubButtonSerializer(data=request.data, context={'request': request})  # Pass request in context
    if serializer.is_valid():
        serializer.save()
        return Response({"status": "ok", "message": "Data created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET'])
def list_subbuttons(request):
    """
    List all SubButtons with their associated Enquiry details.
    - If `user_id` and `enquiry_id` are provided, filter by both.
    - If only `user_id` is provided, filter by user's enquiries.
    - If only `enquiry_id` is provided, filter by the specific enquiry.
    """
    user_id = request.GET.get('user_id')  
    enquiry_id = request.GET.get('enquiry_id') 

    subbuttons = SubButton.objects.select_related('enquiry')

    if user_id and enquiry_id:
        subbuttons = subbuttons.filter(enquiry__user_id=user_id, enquiry_id=enquiry_id)
    elif user_id:
        subbuttons = subbuttons.filter(enquiry__user_id=user_id)
    elif enquiry_id:
        subbuttons = subbuttons.filter(enquiry_id=enquiry_id)

    serializer = SubButtonSerializer(subbuttons, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)







@api_view(['GET'])
def subbutton_detail(request, pk):
    """
    Retrieve a single SubButton by ID, including its associated Enquiry details.
    """
    subbutton = get_object_or_404(SubButton, pk=pk)
    serializer = SubButtonSerializer(subbutton, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_subbutton(request, pk):
    """
    Delete a specific SubButton by ID.
    """
    subbutton = get_object_or_404(SubButton, pk=pk)
    subbutton.delete()
    return Response({"message": "SubButton deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['PUT', 'PATCH'])
def update_subbutton(request, pk):
    """
    Update a specific SubButton by ID.
    - `PUT` requires all fields.
    - `PATCH` allows partial updates.
    """
    subbutton = get_object_or_404(SubButton, pk=pk)
    
    serializer = SubButtonSerializer(subbutton, data=request.data, partial=True, context={'request': request})  

    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "SubButton updated successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def create_enquiry_details(request):
    subheading_id = request.data.get("subheading")  

    if not subheading_id:
        return Response({"error": "subheading is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        subheading = SubButton.objects.get(id=subheading_id)  
    except SubButton.DoesNotExist:
        return Response({"error": "Invalid subheading ID"}, status=status.HTTP_400_BAD_REQUEST)

    enquiry_data = request.data.copy()
    enquiry_data["subheading"] = subheading.id  

    # ✅ Pass request in context
    serializer = EnquiryDetailsSerializer(data=enquiry_data, context={"request": request})  

    if serializer.is_valid():
        serializer.save(subheading=subheading)  
        return Response({"status":"ok","message": "EnquiryDetails created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def list_enquiry_details(request):
    enquiries = EnquiryDetails.objects.all()
    serializer = EnquiryDetailsSerializer(enquiries, many=True, context={"request": request})
    return Response({"status": "ok", "data": serializer.data}, status=status.HTTP_200_OK)



@api_view(['PUT', 'PATCH'])
def update_enquiry_details(request, enquiry_id):
    try:
        enquiry = EnquiryDetails.objects.get(id=enquiry_id)
    except EnquiryDetails.DoesNotExist:
        return Response({"error": "EnquiryDetails not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = EnquiryDetailsSerializer(enquiry, data=request.data, partial=True, context={"request": request})

    if serializer.is_valid():
        serializer.save()
        return Response({"status": "ok", "message": "EnquiryDetails updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def enquiry_details(request, enquiry_id):
    try:
        enquiry = EnquiryDetails.objects.get(id=enquiry_id)
    except EnquiryDetails.DoesNotExist:
        return Response({"error": "EnquiryDetails not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = EnquiryDetailsSerializer(enquiry, context={"request": request})
    return Response({"status": "ok", "data": serializer.data}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_enquiry_details(request, enquiry_id):
    try:
        enquiry = EnquiryDetails.objects.get(id=enquiry_id)
    except EnquiryDetails.DoesNotExist:
        return Response({"error": "EnquiryDetails not found"}, status=status.HTTP_404_NOT_FOUND)

    enquiry.delete()
    return Response({"status": "ok", "message": "EnquiryDetails deleted successfully"}, status=status.HTTP_200_OK)


status_flag = {"status": False}

# API to update status (True or False based on request data)
@api_view(['POST'])
def talking_stop(request):
    new_status = request.data.get("status")  # Expecting {"status": True} or {"status": False"}
    
    if new_status in [True, False]:  
        status_flag["status"] = new_status
        return Response({"message": f"Status updated to {new_status}", "status": status_flag["status"]})
    
    return Response({"error": "Invalid status value. Use True or False."}, status=400)

# API to get current status
@api_view(['GET'])
def talking_status(request):
    return Response({"status": status_flag["status"]})


@api_view(['POST'])
def create_navigation(request):
    """Allows both Admin and Users to create navigation"""

    user = request.user if request.user.is_authenticated else None
    data = request.data.copy()
    if user:
        if user.role == "admin":
            user_id = data.get("user")  
            if not user_id:
                return Response({"error": "Admin must select a user."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user_id = user.id
            data["user"] = user_id  

    serializer = NavigationSerializer(data=data, context={'request': request})
    if serializer.is_valid():
        serializer.save()  
        return Response({"status": "ok", "message": "Enquiry created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def edit_navigation(request, navigation_id):
    """Allows both Admin and Users to edit navigation without authentication"""

    try:
        navigation = Navigation.objects.get(id=navigation_id)
    except Navigation.DoesNotExist:
        return Response({"error": "Navigation entry not found."}, status=status.HTTP_404_NOT_FOUND)

    user = request.user if request.user.is_authenticated else None

    if user:
        if user.role != "admin" and navigation.user.id != user.id:
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    serializer = NavigationSerializer(navigation, data=request.data, partial=True, context={'request': request})
    
    if serializer.is_valid():
        serializer.save()
        return Response({"status": "ok", "message": "Navigation updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





@api_view(['GET'])
def list_navigation(request, user_id):
    """Lists navigation items for a specific user"""
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    navigations = Navigation.objects.filter(user=user)
    serializer = NavigationSerializer(navigations, many=True, context={'request': request})
    
    return Response({"status": "ok","message":"data retrieved successfully", "data": serializer.data}, status=status.HTTP_200_OK)


LAST_CLICKED_NAVIGATION_KEY = "last_clicked_navigation"

@api_view(['GET'])
def get_navigation_by_id(request, nav_id):
    """Retrieve a specific navigation item's ID and name when clicked and store it as last clicked"""
    try:
        navigation = Navigation.objects.get(id=nav_id)
        # Store last clicked navigation in cache (memory) with 10 seconds expiration
        cache.set(LAST_CLICKED_NAVIGATION_KEY, {"id": navigation.id,"nav_id":navigation.nav_id, "name": navigation.name}, timeout=30)
    except Navigation.DoesNotExist:
        return Response({"error": "Navigation not found."}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        "status": "ok",
        "message": "Navigation retrieved successfully",
        "data": {
            "id": navigation.id,
            "name": navigation.name,
            "nav_id":navigation.nav_id
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_last_clicked_navigation(request):
    """Retrieve the last clicked navigation from memory, expire after 10 seconds"""
    last_clicked = cache.get(LAST_CLICKED_NAVIGATION_KEY)

    if not last_clicked:
        return Response({"error": "No navigation has been clicked yet or it has expired."}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        "status": "ok",
        "message": "Last clicked navigation retrieved successfully",
        "data": last_clicked
    }, status=status.HTTP_200_OK)


# Define the upload directory
UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, 'stm_files')

# Ensure the entire directory structure exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

@api_view(['POST'])
def upload_stcm_file(request):
    """API to upload .stcm file and replace all existing files in the folder"""
    serializer = STCMFileSerializer(data=request.data)
    
    if serializer.is_valid():
        file = serializer.validated_data['file']
        
        if not file.name.endswith('.stcm'):
            return Response({"error": "Only .stcm files are allowed"}, status=status.HTTP_400_BAD_REQUEST)

        # Remove all existing .stcm files in the directory
        for existing_file in os.listdir(UPLOAD_DIR):
            if existing_file.endswith('.stcm'):
                os.remove(os.path.join(UPLOAD_DIR, existing_file))

        # Define the file path with its original name
        file_path = os.path.join(UPLOAD_DIR, file.name)

        # Save the new file
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        return Response({"message": "File uploaded successfully", "file_name": file.name}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_latest_stcm_file(request):
    """API to get the latest uploaded .stcm file"""
    try:
        # Get all .stcm files in the directory (should be only one file)
        files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith('.stcm')]
        
        if not files:
            return Response({"message": "No .stcm files found"}, status=status.HTTP_404_NOT_FOUND)

        # There should only be one file, so get the first (only) file
        latest_file = files[0]

        # Construct the file URL
        file_url = os.path.join(settings.MEDIA_URL,  'stm_files', latest_file)

        return Response({"latest_file": latest_file, "file_url": request.build_absolute_uri(file_url)})

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Global variable to store volume (default is 50)
robo_volume = 50  

def set_volume(request, robo_id, volume):
    """API to set volume (same for all robots)"""
    global robo_volume  # Use global variable
    try:
        volume = int(volume)  # Ensure volume is an integer
        if 0 <= volume <= 150:
            robo_volume = volume  # Update volume
            return JsonResponse({"message": "Volume updated", "robo_id": robo_id, "current_volume": robo_volume})
        else:
            return JsonResponse({"error": "Volume must be between 0 and 150"}, status=400)
    except ValueError:
        return JsonResponse({"error": "Invalid volume input. Volume must be an integer."}, status=400)

def get_volume(request, robo_id):
    """API to get current volume (same for all robots)"""
    return JsonResponse({"robo_id": robo_id, "current_volume": robo_volume})



MESSAGE_CACHE_KEY = "latest_message_{}"
BUTTON_STATUS_KEY = "button_status_{}"

@api_view(['POST'])
def post_message(request, robot_id: str):
    """API to post a message and store it in cache for 5 minutes for a specific robot"""
    message = request.data.get("message")
    if not message:
        return Response({"error": "Message is required."}, status=status.HTTP_400_BAD_REQUEST)

    cache.set(MESSAGE_CACHE_KEY.format(robot_id), message, timeout=15) 
    return Response({"status": "ok", "message": "Message posted successfully"}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_message(request, robot_id: str):
    """API to get the latest message for a specific robot, or return 'no message' if expired"""
    message = cache.get(MESSAGE_CACHE_KEY.format(robot_id))
    if not message:
        return Response({"status": "ok","message": "no message"}, status=status.HTTP_200_OK)

    return Response({"status": "ok", "message": message}, status=status.HTTP_200_OK)


@api_view(['POST'])
def button_click(request, robot_id: str):
    """API to set button status to true or false for a specific robot, resets after 5 minutes"""
    status_value = request.data.get("status")

    if status_value not in ["true", "false"]:
        return Response({"error": "Invalid status. Use 'true' or 'false'."}, status=status.HTTP_400_BAD_REQUEST)

    cache.set(BUTTON_STATUS_KEY.format(robot_id), status_value, timeout=15)  # Store for 5 minutes
    return Response({"status": "ok", "message": f"Button clicked, status set to {status_value}"}, status=status.HTTP_200_OK)


@api_view(['GET'])
def button_status(request, robot_id: str):
    """API to get button status for a specific robot - 'true', 'false', or 'no message' after expiry"""
    status_value = cache.get(BUTTON_STATUS_KEY.format(robot_id), "no message")  # Default is "no message"
    return Response({"status": status_value}, status=status.HTTP_200_OK)