# Generated by Django 5.1.6 on 2025-02-22 05:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enquiry', '0002_subbutton'),
    ]

    operations = [
        migrations.CreateModel(
            name='EnquiryDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heading', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='enquiry_images/')),
                ('other_headings', models.CharField(blank=True, max_length=255, null=True)),
                ('subheading', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='details', to='enquiry.subbutton')),
            ],
        ),
    ]
