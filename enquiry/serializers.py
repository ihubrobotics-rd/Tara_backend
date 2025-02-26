from rest_framework import serializers
from .models import *


class EnquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Enquiry
        fields = ['id', 'user', 'logo', 'heading']

    def to_representation(self, instance):
        """ Convert logo to a link instead of showing raw file data. """
        data = super().to_representation(instance)
        request = self.context.get('request')
        if instance.logo:
            data['logo'] = request.build_absolute_uri(instance.logo.url)
        return data

class SubButtonSerializer(serializers.ModelSerializer):
    enquiry_details = EnquirySerializer(source='enquiry', read_only=True)  
    class Meta:
        model = SubButton
        fields = ['id', 'enquiry', 'enquiry_details', 'subheading']  


class EnquiryDetailsSerializer(serializers.ModelSerializer):
    subheading = SubButtonSerializer(read_only=True)

    class Meta:
        model = EnquiryDetails
        fields = ['id', 'heading', 'description', 'image', 'other_headings', 'subheading']



class NavigationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Navigation
        fields = ['id', 'user', 'nav_id', 'name']