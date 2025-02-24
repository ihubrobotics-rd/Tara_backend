from django.shortcuts import render
from accounts.serilaizers import *
from accounts.models import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from django.contrib.auth import get_user_model, logout
from django.utils import timezone
from django.db.models import Q
import os
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
import uuid
import time
import threading

#admin register 
@api_view(['POST'])
def register_user(request):
    """
    Register a new admin user (Approval required by super admin).
    """
    serializer = CustomUserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.validated_data['role'] = 'admin'
        serializer.validated_data['is_approved'] = False  # Not approved by default
        user = serializer.save()
        serialized_data = CustomUserSerializer(user, context={"request": request}).data
        
        return Response(
            {
                "status": "ok",
                "message": "Admin registered successfully. Waiting for super admin approval.",
                "data": serialized_data,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(
        {"status": "error", "errors": serializer.errors},
        status=status.HTTP_400_BAD_REQUEST,
    )

# not approved admins list
@login_required
def unapproved_users_list(request):
    """Displays only users with role 'admin' who are approved or unapproved."""
    if not request.user.is_superuser:  # Allow only superadmins to see this page
        return HttpResponseForbidden("You do not have permission to view this page.")

    unapproved_users = CustomUser.objects.filter(is_approved=False, role='admin')
    approved_users = CustomUser.objects.filter(is_approved=True, role='admin')

    return render(request, 'unapproved_users.html', {
        'approved_users': approved_users,
        'unapproved_users': unapproved_users
    })

@login_required
def toggle_approval(request, user_id):
    """Allow only superadmins to toggle approval status of admins."""
    if not request.user.is_superuser:  # Restrict access to superadmins
        return HttpResponseForbidden("You do not have permission to perform this action.")

    user = get_object_or_404(CustomUser, id=user_id, role='admin')  # Only allow toggling admins
    user.is_approved = not user.is_approved  # Toggle approval status
    user.save()

    return redirect('unapproved_users')


#admin edit
@api_view(['PUT', 'PATCH'])
def edit_admin_user(request, user_id):
    """
    Edit an existing admin user's details.
    """
    try:
        user = CustomUser.objects.get(id=user_id, role='admin')
    except CustomUser.DoesNotExist:
        return Response(
            {"status": "error", "message": "Admin user not found."},
            status=status.HTTP_404_NOT_FOUND,
        )
    username = request.data.get('username', user.username)
    email = request.data.get('email', user.email)
    if CustomUser.objects.filter(Q(username=username) & ~Q(id=user.id)).exists():
        return Response(
            {"status": "error", "message": "Username already exists."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if CustomUser.objects.filter(Q(email=email) & ~Q(id=user.id)).exists():
        return Response(
            {"status": "error", "message": "Email already exists."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = CustomUserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.validated_data['role'] = 'admin'  
        user = serializer.save()
        serialized_data = CustomUserSerializer(user, context={"request": request}).data
        return Response(
            {
                "status": "ok",
                "message": "Admin user updated successfully.",
                "data": serialized_data,
            },
            status=status.HTTP_200_OK,
        )
    return Response(
        {"status": "error", "errors": serializer.errors},
        status=status.HTTP_400_BAD_REQUEST,
    )

#detail admin
@api_view(['GET'])
def admin_user_detail(request, user_id):
    """
    Retrieve the details of an admin user by user_id.
    """
    try:
       user = CustomUser.objects.get(id=user_id, role='admin')
    except CustomUser.DoesNotExist:
        return Response(
            {"status": "error", "message": "Admin user not found."},
            status=status.HTTP_404_NOT_FOUND,
        )
    serializer = CustomUserSerializer(user, context={"request": request})

    return Response(
        {"status": "ok", "message": "Admin user details retrieved successfully.", "data": serializer.data},
        status=status.HTTP_200_OK,
    )



#login view 
@api_view(['POST'])
def login_user(request):
    """
    Authenticate users and return JWT tokens.
    Admins require super admin approval before login.
    """
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user:
        if user.role == 'admin' and not user.is_approved:  # Check approval only for admins
            return Response(
                {"status": "error", "message": "Super admin approval required for login."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token_lifetime = timedelta(days=30)
        access_token_expiry = datetime.now() + access_token_lifetime

        return Response(
            {
                "status": "ok",
                "message": "Login successful",
                "refresh_token": str(refresh),
                "access_token": str(refresh.access_token),
                "expires_in": access_token_expiry.strftime('%Y-%m-%d %H:%M:%S'),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "profile_pic": request.build_absolute_uri(user.profile_pic.url) if user.profile_pic else None,
                    "role": user.role,
                },
            },
            status=status.HTTP_200_OK,
        )
    else:
        return Response(
            {"status": "error", "message": "Invalid username or password."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    
#user create
@api_view(['POST'])
def create_user_by_admin(request):
    """
    Admin creates a single user with role 'user'.
    """
    serializer = CustomUserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.validated_data['role'] = 'user'
        user = serializer.save()
        serialized_data = CustomUserSerializer(user, context={"request": request}).data
        return Response(
            {
                "status": "ok",
                "message": "User created successfully.",
                "data": serialized_data,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(
        {"status": "error", "errors": serializer.errors},
        status=status.HTTP_400_BAD_REQUEST,
    )


#user edit
@api_view(['PUT'])
def edit_user_by_admin(request, user_id):
    """
    Admin edits an existing user's details, ensuring the role remains 'user'.
    """
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response(
            {"status": "error", "message": "User not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = CustomUserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.validated_data['role'] = 'user'
        updated_user = serializer.save()
        serialized_data = CustomUserSerializer(updated_user, context={"request": request}).data
        return Response(
            {
                "status": "ok",
                "message": "User details updated successfully.",
                "data": serialized_data,
            },
            status=status.HTTP_200_OK,
        )
    return Response(
        {"status": "error", "errors": serializer.errors},
        status=status.HTTP_400_BAD_REQUEST,
    )


#list user
@api_view(['GET'])
def list_users_by_admin(request):
    """
    Admin retrieves a list of all users with role 'user'.
    """
    users = CustomUser.objects.filter(role='user')  
    serializer = CustomUserSerializer(users, many=True, context={"request": request})
    return Response(
        {
            "status": "ok",
            "message": "Users with 'user' role retrieved successfully.",
            "data": serializer.data
        },
        status=status.HTTP_200_OK,
    )

@api_view(['GET'])
def user_detail_by_admin(request, user_id):
    """
    Admin retrieves the details of a user with the role 'user'.
    """
    try:
        # Filter the user by ID and role 'user'
        user = CustomUser.objects.get(id=user_id, role='user')
    except CustomUser.DoesNotExist:
        return Response(
            {"status": "error", "message": "User not found or does not have 'user' role."},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = CustomUserSerializer(user, context={"request": request})
    return Response(
        {
            "status": "ok",
            "message": "User details retrieved successfully.",
            "data": serializer.data
        },
        status=status.HTTP_200_OK,
    )


#delete user
@api_view(['DELETE'])
def delete_user_by_admin(request, user_id):
    """
    Admin deletes an existing user.
    """
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response(
            {"status": "error", "message": "User not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    user.delete()
    return Response(
        {"status": "ok", "message": "User deleted successfully."},
        status=status.HTTP_200_OK,  # Changed to HTTP_200_OK
    )


#forgott password email get
@api_view(['POST'])
def forgot_password(request):
    if request.method == 'POST':
        email = request.data.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            otp = random.randint(100000, 999999)
            user.otp = otp
            user.save()  
            subject = 'Your OTP for Password Reset'
            message = f'Hello ,\n\nYour OTP for resetting the password is {otp}. It is valid for 10 minutes.'
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False)
            return Response({'message': 'OTP has been sent to your email', 'user_id': user.pk}, status=status.HTTP_200_OK)
        
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    return Response({'error': 'Invalid request method'}, status=status.HTTP_400_BAD_REQUEST)


#verify otp
@api_view(['POST'])
def verify_otp(request, user_id):  
    if request.method == 'POST':
        otp_entered = request.data.get('otp_entered')  
        print(otp_entered)
        if not otp_entered:
            return Response({'error': 'OTP is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = CustomUser.objects.get(pk=user_id)
            if str(otp_entered) == str(user.otp):
                user.otp = None  
                user.save() 
                return Response({'message': 'OTP verified successfully. You can now reset your password.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
        
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    return Response({'error': 'Invalid request method'}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def set_new_password(request, user_id):  
    if request.method == 'POST':
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        if not new_password or not confirm_password:
            return Response({'error': 'Both new password and confirm password are required'}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

        try:
          
            user = CustomUser.objects.get(pk=user_id)

            user.set_password(new_password)
            user.save()

            return Response({'message': 'Password has been reset successfully'}, status=status.HTTP_200_OK)
        
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    return Response({'error': 'Invalid request method'}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def logout_user(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        logout(request)
        user.last_logout = timezone.now()
        user.save()

        return Response({"status":"ok","message": f"User successfully logged out."}, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    

#add bg image


@api_view(['POST'])
def upload_background_image(request, user_id):
    if request.method == 'POST' and request.FILES.get('background_image'):
        background_image = request.FILES['background_image']
        
        # Define the directory to store the user's background images
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'background_image', str(user_id))
        os.makedirs(upload_dir, exist_ok=True)

        # Get the path for the current image file
        file_path = os.path.join(upload_dir, background_image.name)
        
        # Check if file exists and remove the old one (replace it with the new one)
        if os.path.exists(file_path):
            print(f"Removing old image: {file_path}")  # Debug log
            os.remove(file_path)

        # Initialize FileSystemStorage to save the file
        fs = FileSystemStorage(location=upload_dir)

        # Save the new background image
        fs.save(background_image.name, background_image)

        # Create the absolute URL for the uploaded image
        base_url = request.build_absolute_uri('/')  # Full domain (e.g., http://127.0.0.1:8000/)
        image_url = base_url + 'profile_pics/background_image/' + str(user_id) + '/' + background_image.name

        return Response({
            'status': 'ok',
            'message': 'Background image uploaded successfully and replaced the old one.',
            'user_id': user_id,
            'background_image_url': image_url
        }, status=status.HTTP_200_OK)

    return Response({'error': 'No file uploaded or invalid request.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def list_background_images(request, user_id):
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'background_image', str(user_id))
    if os.path.exists(upload_dir):
        files = os.listdir(upload_dir)
        files.sort(key=lambda x: os.path.getmtime(os.path.join(upload_dir, x)), reverse=True)
        if files:
            latest_file = files[0]
            file_path = os.path.join(upload_dir, latest_file)
            if os.path.isfile(file_path):
                base_url = request.build_absolute_uri('/')  
                image_url = base_url + 'profile_pics/background_image/' + str(user_id) + '/' + latest_file

                return Response({
                    'status': 'ok',
                    'user_id': user_id,
                    'background_image': image_url
                }, status=status.HTTP_200_OK)

    return Response({
        'status': 'ok',
        'message': 'No background image found for this user.'
    }, status=status.HTTP_200_OK)


def superadmin_login(request):
    if request.user.is_authenticated:
       
        if request.user.is_superuser:
            return redirect('upload_zip')  
        else:
            return HttpResponseForbidden("You are not authorized to view this page.")
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('upload_zip')  
        else:
            messages.error(request, 'Invalid credentials or you are not a superadmin.')
    
    return render(request, 'superadmin_login.html')

def superadmin_logout(request):
    logout(request)  # Logs out the user
    return redirect('superadmin_login') 


# robot power on 
ROBOT_STATUS = {"is_on": False}

@api_view(['POST'])
def turn_on(request):
    ROBOT_STATUS["is_on"] = True
    return Response({"message": "Robot turned ON", "status": "ON"})

# robot power off
@api_view(['POST'])
def turn_off(request):
    ROBOT_STATUS["is_on"] = False
    return Response({"message": "Robot turned OFF", "status": "OFF"})

# robot power status
@api_view(['GET'])
def robot_status(request):
    return Response({"status": "ON" if ROBOT_STATUS["is_on"] else "OFF"})


STATUS = {"state": "UNKNOWN", "last_updated": datetime.utcnow()}

def monitor_status():
    """
    Background thread to check if the status is unchanged for 10 seconds.
    If unchanged, update the status to "NO_FACE".
    """
    while True:
        time.sleep(10)  # Check every 10 seconds
        if (datetime.utcnow() - STATUS["last_updated"]).total_seconds() >= 10:
            STATUS["state"] = "NO_FACE"
            STATUS["last_updated"] = datetime.utcnow()

# Start the background monitoring thread
thread = threading.Thread(target=monitor_status, daemon=True)
thread.start()

@api_view(['POST'])
def update_status(request):
    """
    Update the status.
    - If "status" is "UNKNOWN", update to "UNKNOWN".
    - If "status" is "NO_FACE", update to "NO_FACE".
    - If "status" is anything else, update to "KNOWN".
    - If the status is unchanged for 10 seconds, it automatically updates to "NO_FACE".
    """
    new_status = request.data.get("status", "").strip().upper()

    if new_status == STATUS["state"]:
        # If status remains the same, do not update the timestamp
        return Response({
            "message": f"Status remains {STATUS['state']}",
            "status": STATUS["state"]
        })

    # Update status and timestamp
    if new_status == "UNKNOWN":
        STATUS["state"] = "UNKNOWN"
    elif new_status == "NO_FACE":
        STATUS["state"] = "NO_FACE"
    else:
        STATUS["state"] = "KNOWN"

    STATUS["last_updated"] = datetime.utcnow()

    return Response({
        "message": f"Status updated to {STATUS['state']}",
        "status": STATUS["state"]
    })

@api_view(['GET'])
def get_status(request):
    """
    Retrieve the current status.
    """
    return Response({"status": STATUS["state"]})

#stop button api
# Global variable to store the latest session ID

SESSION_DATA = {"session_id": None, "timestamp": None}

@api_view(['GET'])
def generate_session_id(request):
    """
    Generate a new random session ID, store it, and set an expiration time.
    """
    session_id = str(uuid.uuid4())  
    SESSION_DATA["session_id"] = session_id
    SESSION_DATA["timestamp"] = time.time()  # Store the current timestamp

    return Response({
        "status": "ok",
        "message": "Session ID generated successfully",
        "session_id": session_id
    })

@api_view(['GET'])
def get_session_id(request):
    """
    Retrieve the last generated session ID.
    If more than 30 seconds have passed, expire the session ID.
    """
    if SESSION_DATA["session_id"] is None:
        return Response({"error": "No session ID generated yet."}, status=404)

    current_time = time.time()
    elapsed_time = current_time - SESSION_DATA["timestamp"]

    if elapsed_time > 30:  # Check if 5 seconds have passed
        SESSION_DATA["session_id"] = None
        SESSION_DATA["timestamp"] = None
        return Response({"error": "Session ID expired."}, status=403)

    return Response({"session_id": SESSION_DATA["session_id"]})



VIDEO_STATUS = {
    "status": False,
    "last_updated": time.time()  # Store last updated timestamp
}

@api_view(['GET'])
def check_video_status(request):
    """
    Returns the current video status.
    If status is False → Response: "Not Take Video"
    If status is True → Response: "Take Video"
    """
    if VIDEO_STATUS["status"]:
        return Response({"status": True, "message": "Take Video"}, status=status.HTTP_200_OK)
    else:
        return Response({"status": False, "message": "Not Take Video"}, status=status.HTTP_200_OK)

@api_view(['POST'])
def update_video_status(request):
    """
    Updates the video status based on the provided JSON data.
    Expected JSON: { "status": true/false }
    
    Also updates the last_updated timestamp.
    """
    new_status = request.data.get("status")

    if isinstance(new_status, bool):  # Ensures it's a boolean value
        VIDEO_STATUS["status"] = new_status
        VIDEO_STATUS["last_updated"] = time.time()  # Update timestamp
        return Response({"message": "Status updated", "status": new_status}, status=status.HTTP_200_OK)
    
    return Response({"error": "Invalid data. Provide 'status' as true/false."}, status=status.HTTP_400_BAD_REQUEST)