from django.urls import path
from .views import *


urlpatterns = [
    path('add/enquiries/', create_enquiry, name='create_enquiry'),
    path('list/enquiries/', list_enquiries, name='list-enquiries'),
    path('enquiry/edit/<int:enquiry_id>/', edit_enquiry, name='edit_enquiry'),
    path('enquiry/detail/<int:enquiry_id>/', enquiry_detail, name='enquiry_detail'),
    path('enquiry/delete/<int:enquiry_id>/', delete_enquiry, name='delete_enquiry'),


    path('subbutton/create/', create_subbutton, name='create_subbutton'),
    path('subbutton/list/', list_subbuttons, name='list_subbuttons'),
    path('subbutton/detail/<int:pk>/', subbutton_detail, name='subbutton_detail'),
    path('subbutton/delete/<int:pk>/', delete_subbutton, name='delete_subbutton'),
    path('subbutton/edit/<int:pk>/', update_subbutton, name='update_subbutton'),

    path('create/enquiry/details/', create_enquiry_details, name='create-enquiry-details'),
    path('enquiry/details/list/', list_enquiry_details, name='list-enquiry'),
    path('enquiry/update/<int:enquiry_id>/', update_enquiry_details, name='update-enquiry'),
    path('enquiry/details/<int:enquiry_id>/', enquiry_details, name='detail-enquiry'),
    path('enquiry/details/delete/<int:enquiry_id>/', delete_enquiry_details, name='delete-enquiry'),

    path('talk/stop/update/', talking_stop, name='talking_stop_update'),
    path('talk/status/',talking_status,name='talk_status'),

    path('navigation/create/', create_navigation, name='create_navigation'),
    path('navigation/list/<int:user_id>/', list_navigation, name='list_navigation'),
    path('navigation/<int:nav_id>/', get_navigation_by_id, name='get_navigation_by_id'),
    path('navigation/last-clicked/', get_last_clicked_navigation, name='get_last_clicked_navigation'),
]