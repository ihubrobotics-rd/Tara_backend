# Generated by Django 5.1.1 on 2025-02-11 04:30

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employee_id', models.CharField(blank=True, max_length=100, null=True)),
                ('employee_name', models.CharField(blank=True, max_length=200, null=True)),
                ('designation', models.CharField(blank=True, max_length=300, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Punch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, null=True)),
                ('punch_in', models.TimeField(blank=True, null=True)),
                ('punch_out', models.TimeField(blank=True, null=True)),
                ('employee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='robot.employee')),
            ],
        ),
        migrations.CreateModel(
            name='Robot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('robo_name', models.CharField(max_length=255)),
                ('image', models.FileField(blank=True, null=True, upload_to='robo_image/')),
                ('robo_id', models.CharField(max_length=100, unique=True)),
                ('active_status', models.BooleanField(default=False)),
                ('subscription', models.BooleanField(default=False)),
                ('battery_status', models.CharField(blank=True, max_length=100, null=True)),
                ('working_time', models.CharField(blank=True, max_length=200, null=True)),
                ('position', models.CharField(blank=True, max_length=200, null=True)),
                ('language', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='robots', to='robot.language')),
            ],
        ),
        migrations.CreateModel(
            name='PurchaseRobot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('maintenance_hours', models.CharField(blank=True, max_length=200, null=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('robot', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='robot.robot')),
            ],
        ),
        migrations.CreateModel(
            name='NewCustomers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(blank=True, max_length=300, null=True)),
                ('session_id', models.CharField(blank=True, max_length=200, null=True, unique=True)),
                ('gender', models.CharField(blank=True, max_length=200, null=True)),
                ('time_stamp', models.TimeField(blank=True, max_length=200, null=True)),
                ('purpose', models.CharField(blank=True, max_length=500, null=True)),
                ('summery', models.TextField(blank=True, null=True)),
                ('robot', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='robot.robot')),
            ],
        ),
        migrations.CreateModel(
            name='RobotFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zip_file', models.FileField(upload_to='robot_zips/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('robot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='robot.robot')),
            ],
        ),
    ]
