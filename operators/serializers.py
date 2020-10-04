from rest_framework import serializers
from operators.models import TourOperator, Itinerary, Month
from operators.models import ItineraryType

from places.models import Activity
from places.serializers import CountryIndexSimpleSerializer, ActivitySimpleSerializer, CountrySerializer

from photos.models import Photo

from datetime import datetime, timedelta

from users.models import Fav

# TODO: [1] move it to model
from ads.models import Ad
from django.db.models import Q

# TODO: FOR DEBUG. Remove later #
# class MonthSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Month
#         fields = '__all__'

class TourOperatorSerializer(serializers.ModelSerializer):
    flags = CountryIndexSimpleSerializer(source='country_indexes', read_only=True, many=True)
    tours_count = serializers.SerializerMethodField('_tours_count')
    is_fav = serializers.SerializerMethodField('_is_fav')
    new_yas_score = serializers.IntegerField()
    headquarter = CountrySerializer(source='headquarters', read_only=True, many=False)

    def _tours_count(self, obj):
        return Itinerary.objects.filter(tour_operator_id = obj.id).count()

    def _is_fav(self, obj):
        request = self.context['request']
        if not request.user.is_authenticated and not 'uuid' in request.session:
            return False
        if request.user.is_authenticated:
            fav = Fav.objects.filter(user = request.user, tour_operator=obj, date_deleted__isnull=True).first()
            return fav != None
        if 'uuid' in request.session:
            session_uuid = request.session['uuid']
            fav = Fav.objects.filter(uuid = session_uuid, tour_operator=obj, date_deleted__isnull=True).first()
            return fav != None

    class Meta:
        model = TourOperator
        # fields = '__all__'
        fields = ['id','slug', 'name', 'logo', 'average_rating', 'reviews_count', 'yas_score', 
        'tours_count', 'flags', 'is_fav', 'quick_to_respond', 'is_featured','new_yas_score',
        'headquarter']

class ItinerarySerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(read_only=True, source="tour_operator.name")
    flags = CountryIndexSimpleSerializer(source='country_indexes', read_only=True, many=True)
    focus_activities = serializers.SerializerMethodField('_focus_activities')
    # is_featured = serializers.SerializerMethodField('_featured')
    main_features = serializers.SerializerMethodField('_main_features')
    is_fav = serializers.SerializerMethodField('_is_fav')
    yas_score = serializers.IntegerField()
    thumbnail = serializers.SerializerMethodField('get_thumbnail')
    
    def _focus_activities(self, obj):
        activities = []
        try:
            if obj.safari_focus_activity:
                activities += [obj.safari_focus_activity] 
            if obj.non_safari_focus_activity:
                activities += [obj.non_safari_focus_activity]
            if obj.secondary_focus_activity and obj.secondary_focus_activity.exists():
                activities += list(obj.secondary_focus_activity.all())
            activities = activities[:3]
        except Activity.DoesNotExist:
            pass
        label = ''
        for i, activity in enumerate(activities):
            label = label + activity.name_short
            if i < len(activities) - 1: label = label + ', '
        return label

    # TODO: [1] move it to model
    # def _featured(self, obj):
    #     from_date = self.context['request'].query_params.get('from_date', None)
    #     to_date = self.context['request'].query_params.get('to_date', None)
    #     # TODO: can I give and use params in a best way?
    #     if from_date: from_date = datetime.strftime(datetime.strptime(from_date, '%m/%d/%Y'), '%Y-%m-%d')
    #     if to_date: to_date = datetime.strftime(datetime.strptime(to_date, '%m/%d/%Y'), '%Y-%m-%d')

    #     is_featured = False

    #     if from_date or to_date:
    #         query = Q()
    #         query &= Q(itinerary_id = obj.id)
    #         query &= Q(is_active = True)
    #         if from_date: query &= Q(date_start__contains = from_date)
    #         if to_date: query &= Q(date_end__contains = to_date)
    #         ads = Ad.objects.filter(query)
    #         is_featured = ads.first() != None

    #     return is_featured
    
    def _main_features(self, obj):
        itinerary_type = obj.itinerary_type.name.split(', ')
        itinerary_type = itinerary_type[2].split(' ')[0].title() + ', ' + itinerary_type[0].replace('A ', '')
        luxury_level = obj.tour_operator.luxury_level.replace('_LEVEL', '').title() + '-luxury'
        if obj.activity_level_name:
            activity = obj.activity_level_name + ' activity'
        else:
            activity = False
        if activity:
            return itinerary_type + ' | ' + luxury_level + ' | ' + activity
        else:
            return itinerary_type + ' | ' + luxury_level

    def _is_fav(self, obj):
        request = self.context['request']
        if not request.user.is_authenticated and not 'uuid' in request.session:
            return False
        if request.user.is_authenticated:
            fav = Fav.objects.filter(user = request.user, itinerary=obj, date_deleted__isnull=True).first()
            return fav != None
        if 'uuid' in request.session:
            session_uuid = request.session['uuid']
            fav = Fav.objects.filter(uuid = session_uuid, itinerary=obj, date_deleted__isnull=True).first()
            return fav != None

    def get_thumbnail(self, obj):
        from core.utils import get_thumbnailer_
        return get_thumbnailer_(obj.image, 'card')

    class Meta:
        model = Itinerary
        # fields = '__all__'
        fields = ['id', 'title', 'title_short', 'slug', 'min_price', 'duration', 
        'tour_operator', 'operator_name', 'flags', 'focus_activities', 'image', 'thumbnail', 
        'is_featured', 'main_features', 'is_fav','yas_score' ]
    

class ItineraryTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItineraryType
        fields = ['id', 'name']