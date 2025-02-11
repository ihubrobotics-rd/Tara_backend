from django.urls import path
from robot.views import *

urlpatterns = [
    path('create/robot/', create_robot, name='create_robot'),
    path('list/robots/', list_robots, name='list_robots'),
    path('update/robot/<str:robo_id>/', update_robot_by_id, name='update_robot'),
    path('delete/robot/<str:robo_id>/', delete_robot, name='delete_robot'),
    path('robot/detail/<str:robo_id>/', robot_detail, name='robot_detail'),

    path('languages/create/', create_language, name='create_language'),
    path('languages/list/', list_languages, name='list_languages'),
    path('languages/edit/<int:pk>/', edit_language, name='edit_language'),
    path('languages/detail/<int:pk>/', language_detail, name='language_detail'),
    path('languages/delete/<int:pk>/', delete_language, name='delete_language'),

    path('get-robots/', get_robots_file, name='get_robots_file'),
    path('update-robots/', update_robots_file, name='update_robots_file'),

    path('sale/robot/', create_purchase_robot, name='sale_robot'),
    path('sale/robots/list/', list_purchase_robots, name='list_purchase_robots'),
    path('edit/sale/robot/<int:pk>/', update_purchase_robot, name='edit_purchase_robot'),
    path('sale/robot/delete/<int:pk>/', delete_purchase_robot, name='delete_purchase_robot'),
    path('sale/user/list/<int:user_id>/', list_purchase_robot_by_user, name='list_purchase_robot_by_user'),

    
    path('new/customer/add/', create_new_customer, name='create_new_customer'),
    path('customers/list/', list_new_customers, name='list_new_customers'),
    path('download/customers/csv/', download_customers_csv, name='download_customers_csv'),
    path('customer/edit/<str:session_id>/', edit_customer_summery, name='edit-customer-summery'),
    path('customer/detail/<str:session_id>/', customer_detail_view, name='customer_detail'),
    
    path('add/employee/', create_employee, name='create-employee'),
    path('list/employee/', list_employees, name='list-employees'),
    path('edit/employee/<str:employee_id>/', edit_employee, name='edit-employee'),
    path('detail/employee/<str:employee_id>/', employee_detail, name='employee-detail'),
    path('employee/delete/<str:employee_id>/', delete_employee, name='delete-employee'),


    path('add/punching/', create_punch, name='create-punch'),
    path('list/punching/', list_punches, name='list_punches'), 
    path('download/punching/csv/', download_csv, name='download_punches'), 
    path('punch_out/edit/<str:employee_id>/', edit_punch_out, name='edit_punch_out'),
    path('delete-punch/<int:punch_id>/', delete_punch, name='delete-punch'),


    path('upload-pdf/<str:robo_id>/', upload_robot_pdf, name='upload_robot_pdf'),
    path('pdf-details/<str:robo_id>/', get_robot_pdf_details, name='get_robot_pdf_details'),
    path('upload/zip/', upload_zip_file, name='upload_zip'),
    path('api/list/zip/<str:robo_id>/', list_zip_files, name='list_zip_files'),

    path("update_status/", update_status, name="update_status"),
    path("list_status/", list_status, name="list_status"),

]