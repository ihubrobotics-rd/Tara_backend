# Generated by Django 5.1.1 on 2025-02-12 04:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('robot', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='robot',
            name='current',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='robot',
            name='energy',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='robot',
            name='power',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='robot',
            name='voltage',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
