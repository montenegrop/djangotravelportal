from django.conf import settings
from analytics.models import Analytic
import os
import IP2Location
import ipaddress


def log_action(request, hit_object=False, activity_type=Analytic.VISIT):
    from analytics.models import Analytic
    import datetime
    data = get_visitor_data(request)
    page_url = request.build_absolute_uri()
    path = request.path
    existent = Analytic.objects.all()
    existent = existent.filter(path=path)
    existent = existent.filter(ip_address=data['ip_address'])
    minutes_ago = datetime.datetime.now() - datetime.timedelta(minutes=settings.MINUTES_AGO_HIT_COUNT)
    existent = existent.filter(date_created__gte=minutes_ago)
    if existent.exists():
        return

    analytic = Analytic(**data)
    if request.user.is_authenticated:
        analytic.user = request.user
    if hit_object:
        analytic.content_object = hit_object
    analytic.page_url = page_url
    analytic.path = path
    analytic.activity_type = activity_type
    analytic.save()


def get_visitor_data(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    device_type = ""
    browser_type = ""
    browser_version = ""
    os_type = ""
    os_version = ""

    if request.user_agent.is_mobile:
        device_type = "Mobile"
    if request.user_agent.is_tablet:
        device_type = "Tablet"
    if request.user_agent.is_pc:
        device_type = "PC"

    browser_type = request.user_agent.browser.family
    browser_version = request.user_agent.browser.version_string
    os_type = request.user_agent.os.family
    os_version = request.user_agent.os.version_string

    context = {
        "ip_address": ip,
        "device_type": device_type,
        "browser_type": browser_type,
        "browser_version": browser_version,
        "os_type": os_type,
        "os_version": os_version,
        'referer': request.META.get('HTTP_REFERER'),
    }
    country_short = get_country_by_ip(ip)
    if country_short:
        context.update({
            'country_short': country_short,
        })
    return context

def get_request_country(request):
    from places.models import Country
    ip = get_visitor_data(request)['ip_address']
    try:
        iso = get_country_by_ip(ip)
        country = Country.objects.get(iso=iso)
        if country:
            return country
    except Country.DoesNotExist:
        return False
    return False

def get_country_by_ip(ip):
    ip_ver = ipaddress.ip_address(str(ip))
    if ip_ver.version == 4:
        if os.path.exists(settings.IPV6_IP2LOCATION_PATH):
            database = IP2Location.IP2Location(settings.IPV6_IP2LOCATION_PATH)
            rec = database.get_all(ip)
            return rec.country_short
    else:
        if os.path.exists(settings.IPV4_IP2LOCATION_PATH):
            database = IP2Location.IP2Location(settings.IPV4_IP2LOCATION_PATH)
            rec = database.get_all(ip)
            return rec.country_short
    return False
