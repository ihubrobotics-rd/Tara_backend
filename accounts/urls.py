from django.urls import path
from accounts.views import *

urlpatterns = [
    path('register/', register_user, name='register_user'),
    path('edit/admin/<int:user_id>/', edit_admin_user, name='edit_admin_user'),
    path('admin/detail/<int:user_id>/', admin_user_detail, name='admin_user_detail'),
    path('login/', login_user, name='login_user'),
    path('logout/<int:user_id>/', logout_user, name='logout_user'),


    path('forgot/password/', forgot_password, name='forgot_password'),
    path('verify/otp/<int:user_id>/', verify_otp, name='verify_otp'),
    path('new/password/<int:user_id>/', set_new_password, name='set_new_password'),  

    path('user_create/',create_user_by_admin,name="user_create"),
    path('edit_user/<int:user_id>/', edit_user_by_admin, name='edit_user'),
    path('delete_user/<int:user_id>/', delete_user_by_admin, name='delete_user'),
    path('list_users/', list_users_by_admin, name='list_users'),
    path('user_detail/<int:user_id>/', user_detail_by_admin, name='user_detail'),  

    path('upload/background/<int:user_id>/', upload_background_image, name='upload_background_image'),
    path('list/background/images/<int:user_id>/', list_background_images, name='list_background_images'),

    path('login/admin/',superadmin_login, name='superadmin_login'),
    path('logout/', superadmin_logout, name='superadmin_logout'),
    path('unapproved/admin/', unapproved_users_list, name='unapproved_users'),
    path('toggle-approval/<int:user_id>/', toggle_approval, name='toggle_approval'),


    path('robot/on/', turn_on, name='turn_on'),
    path('robot/off/', turn_off, name='turn_off'),
    path('robot/status/', robot_status, name='robot_status'),

    path('customer/status/', update_status, name='update_status'),
    path('status/get/', get_status, name='get_status'),
    
    path('session_id/generate/', generate_session_id, name='generate_session_id'),
    path('session/get/', get_session_id, name='get_session_id'),

    path('video/status/', check_video_status, name='check_video_status'),  # GET: Check status
    path('video/update/', update_video_status, name='update_video_status'),  # POST: Update status
]



