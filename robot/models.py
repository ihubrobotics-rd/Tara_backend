from django.db import models
from accounts.models import CustomUser

class Robot(models.Model):
    robo_name = models.CharField(max_length=255)
    image = models.FileField(upload_to='robo_image/', null=True, blank=True)
    robo_id = models.CharField(max_length=100, unique=True)
    active_status = models.BooleanField(default=False)
    subscription = models.BooleanField(default=False)
    battery_status = models.CharField(max_length=100, null=True, blank=True)
    working_time = models.CharField(max_length=200, null=True, blank=True)
    position = models.CharField(max_length=200, null=True, blank=True)
    language = models.ForeignKey('Language', related_name='robots', on_delete=models.CASCADE, null=True, blank=True)
    voltage=models.CharField(max_length=200,null=True,blank=True)
    current=models.CharField(max_length=200,null=True,blank=True)
    power=models.CharField(max_length=200,null=True,blank=True)
    energy=models.CharField(max_length=200,null=True,blank=True)
    quality=models.CharField(max_length=200,null=True,blank=True)
    map=models.BooleanField(default=False)
    emergency_stop=models.BooleanField(default=False)
    motor_brake_released=models.BooleanField(default=False)
    ready_to_navigate=models.BooleanField(default=False)
    volume=models.IntegerField(default=50)

    def __str__(self):
        return self.robo_name

   
    
class Language(models.Model):
    language=models.CharField(max_length=200,null=True,blank=True)
    def __str__(self):
        return self.language or "Unnamed Language"
    

    
    
class PurchaseRobot(models.Model):
    robot=models.ForeignKey(Robot,on_delete=models.CASCADE,null=True,blank=True)
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,blank=True)
    date=models.DateField(auto_now_add=True)
    end_date=models.DateField(null=True,blank=True)
    maintenance_hours=models.CharField(null=True,blank=True,max_length=200)
    def __str__(self):
        return self.robot


class NewCustomers(models.Model):
    username=models.CharField(max_length=300,null=True,blank=True)
    session_id=models.CharField(max_length=200,null=True,blank=True,unique=True)
    gender=models.CharField(max_length=200,null=True,blank=True)
    time_stamp=models.TimeField(max_length=200,null=True,blank=True)
    purpose=models.CharField(max_length=500,null=True,blank=True)
    robot=models.ForeignKey(Robot,on_delete=models.CASCADE,null=True,blank=True)
    summery=models.TextField(null=True,blank=True)

    def __str__(self):
        return self.username
    
class Employee(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,blank=True)
    employee_id=models.CharField(max_length=100,null=True,blank=True,unique=True)
    employee_name=models.CharField(max_length=200,null=True,blank=True)
    designation=models.CharField(max_length=300,null=True,blank=True)

    def __str__(self):
        return self.employee_id
    
class Punch(models.Model):
    employee=models.ForeignKey(Employee,on_delete=models.CASCADE,null=True,blank=True)
    date=models.DateField(null=True,blank=True)
    punch_in=models.TimeField(null=True,blank=True)
    punch_out=models.TimeField(null=True,blank=True)

    def __str__(self):
        return self.employee
    
class RobotFile(models.Model):
    robot = models.ForeignKey(Robot, related_name='files', on_delete=models.CASCADE)
    zip_file = models.FileField(upload_to='robot_zips/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.robot.robo_name} - {self.zip_file.name}"


class VideoStatus(models.Model):
    listening = models.BooleanField(default=False)
    waiting = models.BooleanField(default=False)
    speaking = models.BooleanField(default=False)

    def set_status(self, active_key):
        """
        Update the status so that only one field is True at a time.
        """
        for field in ["listening", "waiting", "speaking"]:
            setattr(self, field, field == active_key)
        self.save()