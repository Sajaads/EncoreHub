from rest_framework import serializers
from concert_management.models import Concert

class ConcertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concert
        fields = '__all__'