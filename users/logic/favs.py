
from operators.models import TourOperator, Itinerary
from users.models import Fav
import uuid

def get_favs(request):
    from django.db.models import Q
    #to avoid duplicates
    if request.user.is_authenticated:
        if not 'uuid' in request.session: 
            request.session['uuid'] = str(uuid.uuid1())
        favs = request.user.favs.filter(Q(date_deleted__isnull=True) | Q(uuid=request.session['uuid']))
    else:
        if not 'uuid' in request.session: 
            request.session['uuid'] = str(uuid.uuid1())
        favs = Fav.objects.filter(uuid=request.session['uuid'])
        favs = favs.filter(date_deleted__isnull=True)
    return favs

def get_favs_count(request):
    favs = get_favs(request)
    favs_to = favs.filter(tour_operator__isnull=False).filter(itinerary__isnull=True).values_list('tour_operator__pk', flat=True)
    favs_it = favs.filter(itinerary__isnull=False).values_list('itinerary__pk', flat=True)
    tour_operators = TourOperator.objects.filter(pk__in=favs_to)
    itineraries = Itinerary.objects.filter(pk__in=favs_it)
    favs_count = itineraries.count() + tour_operators.count()
    return favs_count

def get_to_favs(request):
    favs = get_favs(request)
    favs_to = favs.filter(tour_operator__isnull=False).filter(itinerary__isnull=True).values_list('tour_operator__pk', flat=True)
    tour_operators = TourOperator.objects.filter(pk__in=favs_to)
    return tour_operators

def get_it_favs(request):
    favs = get_favs(request)
    favs_it = favs.filter(itinerary__isnull=False).values_list('itinerary__pk', flat=True)
    itineraries = Itinerary.objects.filter(pk__in=favs_it)
    return itineraries

def get_to_favs_count(request):
    favs_to = get_to_favs(request)
    return favs_to.count()

def get_it_count_favs(request):
    favs_it = get_it_favs(request)
    return favs_it.count()
