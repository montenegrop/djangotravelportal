from rest_framework import serializers
from places.models import CountryIndex, Park, Activity, Language, Country

class CountryIndexSimpleSerializer(serializers.ModelSerializer):
    tag = serializers.ReadOnlyField(default='country')
    base_id = serializers.SerializerMethodField()
    mini_description = serializers.SerializerMethodField()
    flag_url = serializers.SerializerMethodField()
    @staticmethod
    def get_mini_description(obj):
        return "Country"

    @staticmethod
    def get_base_id(obj):
        return obj.id

    @staticmethod
    def get_flag_url(obj):
        return obj.flag.url

    class Meta:
        model = CountryIndex
        fields = ['id', 'name_short', 'flag_url','tag', 'base_id', 'slug','mini_description', 'is_top']

class ParkSimpleSerializer(serializers.ModelSerializer):
    tag = serializers.ReadOnlyField(default='park')
    base_id = serializers.SerializerMethodField()
    mini_description = serializers.SerializerMethodField()
    
    @staticmethod
    def get_mini_description(obj):
        return "Park in {}".format(obj.country_indexes.first().name_short)

    @staticmethod
    def get_base_id(obj):
        return obj.id

    class Meta:
        model = Park
        fields = ['id', 'name_short', 'tag', 'base_id', 'slug','mini_description', 'is_top']

class ActivitySimpleSerializer(serializers.ModelSerializer):
  class Meta:
    model = Activity
    fields = ['id', 'name_short']

class LanguageSerializer(serializers.ModelSerializer):
  class Meta:
    model = Language
    fields = ['id', 'name']

class CountrySerializer(serializers.ModelSerializer):
  class Meta:
    model = Country
    fields = ['id', 'name', 'flag_flat']
