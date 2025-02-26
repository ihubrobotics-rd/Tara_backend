from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Enquiry
from .serializers import *
from django.shortcuts import get_object_or_404
from django.core.cache import cache

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
    - If `user_id` is provided in query parameters, filter by the user's enquiries.
    - If `enquiry_id` is provided, filter by the specific enquiry.
    """
    user_id = request.GET.get('user_id')  # Get user_id from query parameters
    enquiry_id = request.GET.get('enquiry_id')  # Get enquiry_id from query parameters

    subbuttons = SubButton.objects.select_related('enquiry').all()

    if user_id:
        subbuttons = subbuttons.filter(enquiry__user_id=user_id)
    
    if enquiry_id:
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
        cache.set(LAST_CLICKED_NAVIGATION_KEY, {"id": navigation.id, "name": navigation.name}, timeout=30)
    except Navigation.DoesNotExist:
        return Response({"error": "Navigation not found."}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        "status": "ok",
        "message": "Navigation retrieved successfully",
        "data": {
            "id": navigation.id,
            "name": navigation.name
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