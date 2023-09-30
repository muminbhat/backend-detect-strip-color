from rest_framework import serializers
from .models import Newsletter

class NewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsletter
        fields = '__all__'

    def validate_email(self, value):
        """
        Check if an entry with the same email already exists.
        """
        if Newsletter.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email is already registered.')
        return value