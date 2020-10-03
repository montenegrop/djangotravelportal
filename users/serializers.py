from rest_framework import serializers
from operators.models import Itinerary
from django.contrib.auth.models import User
from users.models import Fav

class FavSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fav
        fields = '__all__'